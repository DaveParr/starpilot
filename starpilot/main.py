import os
import shutil
from enum import Enum

import click
import dotenv
import typer
from github import Github
from langchain.chains import RetrievalQA
from langchain.chains.query_constructor.base import (
    AttributeInfo,
    get_query_constructor_prompt,
    load_query_constructor_runnable,
)
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import GPT4AllEmbeddings
from langchain.llms import GPT4All
from langchain.prompts import PromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.vectorstores import Chroma
from rich import print
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Optional

import starpilot.utils.utils as utils

# Setup for icecream
try:
    from icecream import ic, install

    install()
except Exception as e:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


# Environment variables
dotenv.load_dotenv()

VECTORSTORE_PATH = "./vectorstore-chroma"

try:
    git_hub_key = os.getenv("GITHUB_API_KEY")
    GITHUB_CONNECTION = Github(git_hub_key)
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

    typer.echo("Please enter your GitHub API key")
    github_api_key = typer.prompt('GitHub API key with quotes e.g. "ghp_..."')
    typer.echo("Please enter your OpenAI API key")
    openai_api_key = typer.prompt('OpenAI API key with quotes e.g. "sk_..."')

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

    repos = utils.get_user_starred_repos(
        user=user,
        g=GITHUB_CONNECTION,
        num_repos=k,
    )

    repo_contents = utils.get_repo_contents(
        repos=repos,
        g=GITHUB_CONNECTION,
    )

    utils.save_repo_contents_to_disk(repo_contents=repo_contents)

    vectorstore_path = "./vectorstore-chroma"

    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    # IDEA: Set the collection to be the user's name, then only rebuild the vector store for that user, and allow the user to search a different users stars without a rebuild
    # IDEA: Compare the results of the existing vectorstore to the results of the GitHub API and only CRUD the files that have changed

    repo_documents = utils.prepare_documents()

    Chroma.from_documents(
        documents=repo_documents,
        embedding=GPT4AllEmbeddings(disallowed_special=()),
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
        k=k,
        method=method.value,
        score_threshold=threshold,
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
            openai_api_key=openai_api_key,
        ),
        document_contents=document_contents,
        attribute_info=attribute_info,
        fix_invalid=True,
        allowed_comparators=[
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
        ],  # set to chroma allowed comparators, if this changes, these can (*should*) be updated
    )

    retriever = SelfQueryRetriever(
        query_constructor=chain,
        vectorstore=Chroma(
            persist_directory=VECTORSTORE_PATH, embedding_function=GPT4AllEmbeddings()
        ),
        verbose=True,
    )

    print(utils.create_results_table(retriever.get_relevant_documents(query)))
