import logging
import os
import shutil
from typing import Annotated

import dotenv
import structlog
import typer
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.chains.query_constructor.ir import Comparator
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from rich import print
from typing_extensions import Optional

import starpilot.utils.utils as utils

# Setup for icecream
try:
    from icecream import ic, install

    install()
except Exception:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING)
)
logger = structlog.get_logger()


VECTORSTORE_PATH = "./vectorstore-chroma"

dotenv.load_dotenv(dotenv_path=".env")

# Typer setup
app = typer.Typer()


@app.command()
def setup(
    tracing: Annotated[
        bool, typer.Option(help="Enable tracing with LangSmith")
    ] = False,
):
    """
    Setup the CLI with the required API keys
    """

    env_file = ".env"

    typer.echo(
        """
        Please enter your GitHub API key from https://github.com/settings/tokens
        e.g. ghp_...
        This can be scoped to read:user
        """
    )
    github_api_key = typer.prompt("GitHub API key")
    dotenv.set_key(env_file, "GITHUB_API_KEY", github_api_key)

    typer.echo(
        """
        Please enter your OpenAI API key from https://platform.openai.com/api-keys
        e.g. sk_...
        """
    )
    openai_api_key = typer.prompt("OpenAI API key")
    dotenv.set_key(env_file, "OPENAI_API_KEY", openai_api_key)

    typer.echo(
        """
        Please enter your OpenAI Organization ID from https://platform.openai.com/account/organization
        e.g. org-...
        """
    )
    openai_org_id = typer.prompt("OpenAI Organization ID")
    dotenv.set_key(env_file, "OPENAI_ORG_ID", openai_org_id)

    if tracing:
        typer.echo(
            """
            Please enter your LangSmith API key from hhttps://smith.langchain.com/
            e.g. ls__...
            """
        )
        langsmith_api_key = typer.prompt("LangSmith API key")
        dotenv.set_key(env_file, "LANGCHAIN_API_KEY", langsmith_api_key)
        dotenv.set_key(env_file, "LANGCHAIN_PROJECT", "starpilot")
        dotenv.set_key(env_file, "LANGCHAIN_TRACING_V2", tracing, quote_mode="never")  # type: ignore deliberately abusing quote mode to write the bool type that langsmith expects because https://github.com/theskumar/python-dotenv/issues/86
    else:
        dotenv.set_key(env_file, "LANGCHAIN_TRACING_V2", tracing, quote_mode="never")  # type: ignore deliberately abusing quote mode to write the bool type that langsmith expects because https://github.com/theskumar/python-dotenv/issues/86


# Typer commands
@app.command()
def read(
    user: str,
    k: Optional[int] = typer.Option(500, help="Number of repositories to load"),
) -> None:
    """
    Read stars from GitHub
    """

    GITHUB_API_KEY = os.environ["GITHUB_API_KEY"]

    repos = utils.get_user_starred_repos(
        username=user,
        github_api_key=GITHUB_API_KEY,
    )

    formatted_repos = []
    for repo in repos:
        formatted_repos.append(utils.format_repo(repo))

    utils.save_repo_contents_to_disk(repo_contents=formatted_repos)

    vectorstore_path = "./vectorstore-chroma"

    if os.path.exists(vectorstore_path):
        logger.debug("Removing previous vectorstore", path=vectorstore_path)
        shutil.rmtree(vectorstore_path)

    # # IDEA: Set the collection to be the user's name, then only rebuild the vector store for that user, and allow the user to search a different users stars without a rebuild
    # # IDEA: Compare the results of the existing vectorstore to the results of the GitHub API and only CRUD the files that have changed

    repo_documents = utils.prepare_documents()

    Chroma.from_documents(
        documents=repo_documents,
        embedding=GPT4AllEmbeddings(client=None),
        persist_directory=vectorstore_path,
    )


@app.command()
def shoot(
    query: str,
    method: utils.SearchMethods = typer.Option(
        "similarity", help="The search method to use"
    ),
    k: Optional[int] = typer.Option(
        15, help="Number of results to fetch from the vectorstore"
    ),
):
    """
    An embedding search of the vectorstore
    """

    if not os.path.exists(VECTORSTORE_PATH):
        raise Exception("Please load the stars before shooting")

    retriever = utils.create_retriever(
        vectorstore_path=VECTORSTORE_PATH,
        k=k,  # type: ignore
        method=method.value,  # type: ignore
    )

    print(utils.create_results_table(retriever.get_relevant_documents(query)))


@app.command()
def astrologer(
    query: str,
    k: Optional[int] = typer.Option(
        4, help="Number of results to fetch from the vectorstore"
    ),
):
    """
    A self-query of the vectorstore that allows the user to search for a repo while filtering by attributes

    Example:
    ```
    starpilot astrologer "What can I use to build a web app with Python?"
    starpilot astrologer "Suggest some Rust machine learning crates"
    ```

    """

    if not os.path.exists(VECTORSTORE_PATH):
        raise Exception("Please load the stars before shooting")

    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    OPENAI_ORG_ID = os.environ["OPENAI_ORG_ID"]

    metadata_field_info = [
        # IDEA: create valid specific values on data load for each users content
        AttributeInfo(
            name="languages",
            description="the programming languages of a repo. Example: ['python', 'R', 'Rust']",
            type="string",
        ),
        AttributeInfo(
            name="name",
            description="the name of a repository. Example: 'langchain'",
            type="string",
        ),
        AttributeInfo(
            name="topics",
            description="the topics a repository is tagged with. Example: ['data-science', 'machine-learning', 'python', 'web-development', 'tidyverse']",
            type="string",
        ),
        AttributeInfo(
            name="url",
            description="the url of a repository on GitHub",
            type="string",
        ),
    ]

    document_content_description = "content describing a repository on GitHub"

    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,  # type: ignore
        organization=OPENAI_ORG_ID,
        model="gpt-3.5-turbo",
    )

    # https://python.langchain.com/docs/modules/data_connection/retrievers/self_query#constructing-from-scratch-with-lcel
    # https://github.com/langchain-ai/langchain/blob/master/cookbook/self_query_hotel_search.ipynb

    prompt = get_query_constructor_prompt(
        document_content_description,
        metadata_field_info,
        allowed_comparators=[
            Comparator.EQ,
            Comparator.NE,
            Comparator.GT,
            Comparator.GTE,
            Comparator.LT,
            Comparator.LTE,
        ],
    )
    output_parser = StructuredQueryOutputParser.from_components()

    query_constructor = prompt | llm | output_parser

    ic(query_constructor.invoke({"query": query}))

    from langchain.retrievers.self_query.chroma import ChromaTranslator

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(client=None),
    )

    retriever = SelfQueryRetriever(
        query_constructor=query_constructor,  # type: ignore because it's documented as a pattern https://python.langchain.com/docs/modules/data_connection/retrievers/self_query#constructing-from-scratch-with-lcel:~:text=The%20next%20key,Integrations%20section.
        vectorstore=vectorstore,
        structured_query_translator=ChromaTranslator(),
        search_kwargs={"k": k},
    )

    results = retriever.invoke(query)

    print(utils.create_results_table(results))
