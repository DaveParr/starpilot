import logging
import os
import shutil

import dotenv
import structlog
import typer
from langchain.chains.query_constructor.base import (
    load_query_constructor_runnable,
)
from langchain.chains.query_constructor.ir import Comparator
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import GPT4AllEmbeddings
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.vectorstores import Chroma
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

# Environment variables
dotenv.load_dotenv()

VECTORSTORE_PATH = "./vectorstore-chroma"

try:
    git_hub_key = os.getenv("GITHUB_API_KEY")
except Exception:
    raise Exception("Please create a .env file with your GitHub token")


# Typer setup
app = typer.Typer()


@app.command()
def setup():
    """
    Setup the CLI with the required API keys
    """

    if os.path.exists(".env"):
        os.remove(".env")

    typer.echo(
        """
        Please enter your GitHub API key from https://github.com/settings/tokens
        This can be scoped to read:user
        Use quotes e.g. "ghp_..."
        """
    )
    github_api_key = typer.prompt("GitHub API key")
    typer.echo(
        """
        Please enter your OpenAI API key from https://platform.openai.com/api-keys
        Use quotes e.g. "sk_..."
        """
    )
    openai_api_key = typer.prompt("OpenAI API key")

    with open(".env", "w") as f:
        f.write(f"GITHUB_API_KEY={github_api_key}\n")
        f.write(f"OPENAI_API_KEY={openai_api_key}\n")


# Typer commands
@app.command()
def read(
    user: str,
    k: Optional[int] = typer.Option(500, help="Number of repositories to load"),
) -> None:
    """
    Read stars from GitHub
    """

    if (git_hub_key := os.getenv("GITHUB_API_KEY")) is None:
        raise Exception(
            "Please create a .env file with your GitHub token with the `setup` command"
        )

    repos = utils.get_user_starred_repos(
        username=user,
        github_api_key=git_hub_key,
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
    threshold: Optional[float] = typer.Option(
        0.3, help="The similarity threshold to use"
    ),
):
    """
    Shoot a query at the stars
    """

    if not os.path.exists(VECTORSTORE_PATH):
        raise Exception("Please load the stars before shooting")

    retriever = utils.create_retriever(
        vectorstore_path=VECTORSTORE_PATH,
        k=k,  # type: ignore
        method=method.value,  # type: ignore
        score_threshold=threshold,  # type: ignore
    )

    print(utils.create_results_table(retriever.get_relevant_documents(query)))


@app.command()
def astrologer(
    query: str,
):
    """
    Use SelfQueryRetriever to self-query the vectorstore
    """

    if (openai_api_key := os.getenv("OPENAI_API_KEY")) is None:
        raise Exception(
            "Please create a .env file with your OpenAI API key with the `setup` command"
        )

    attribute_info = [
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

    document_contents = "content describing a repository on GitHub"

    chain = load_query_constructor_runnable(
        llm=ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=openai_api_key,
        ),
        document_contents=document_contents,
        attribute_info=attribute_info,
        fix_invalid=True,
        allowed_comparators=[
            Comparator.EQ,
            Comparator.NE,
            Comparator.GT,
            Comparator.GTE,
            Comparator.LT,
            Comparator.LTE,
        ],  # set to chroma specific allowed comparators, if the vectorstore changes, these can (*should*) be updated
    )

    retriever = SelfQueryRetriever(
        llm_chain=chain,
        vectorstore=Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=GPT4AllEmbeddings(client=None),
        ),
        verbose=True,
    )  # type: ignore

    print(utils.create_results_table(retriever.get_relevant_documents(query)))
