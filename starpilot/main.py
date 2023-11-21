import os
import shutil
from enum import Enum

import dotenv
import typer
from github import Github
from icecream import install
from langchain.chains import RetrievalQA
from langchain.embeddings import GPT4AllEmbeddings
from langchain.llms import GPT4All
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from rich import print
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Optional

import starpilot.utils.utils as utils

# Setup for icecream
try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

install()


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


# Typer commands
@app.command()
def read(
    user: str,
    num_repos: Optional[int] = typer.Option(500, help="Number of repositories to load"),
    include_readmes: Optional[bool] = typer.Option(
        False, help="Include READMEs in the vectorstore"
    ),
) -> None:
    """
    Read stars from GitHub
    """

    repos = utils.get_user_starred_repos(
        user=user,
        g=GITHUB_CONNECTION,
        num_repos=num_repos,
    )

    repo_contents = utils.get_repo_contents(
        repos=repos,
        include_readmes=include_readmes,
        g=GITHUB_CONNECTION,
    )

    utils.save_repo_contents_to_disk(repo_contents=repo_contents)

    vectorstore_path = "./vectorstore-chroma"

    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    # IDEA: Set the collection to be the user's name, then only rebuild the vector store for that user, and allow the user to search a different users stars without a rebuild
    # TODO: Set the document id to be specific to the repo, and then have the topic, description, and readme to be sequenced together
    repo_descriptions = utils.prepare_description_documents()

    Chroma.from_documents(
        documents=repo_descriptions,
        embedding=GPT4AllEmbeddings(disallowed_special=()),
        persist_directory=vectorstore_path,
    )

    repo_topics = utils.prepare_topic_documents()

    Chroma.from_documents(
        documents=repo_topics,
        embedding=GPT4AllEmbeddings(disallowed_special=()),
        persist_directory=vectorstore_path,
    )

    if include_readmes:
        readme_documents = utils.prepare_readme_documents()

        Chroma.from_documents(
            documents=readme_documents,
            embedding=GPT4AllEmbeddings(disallowed_special=()),
            persist_directory=vectorstore_path,
        )


class SearchMethods(Enum):
    similarity = "similarity"
    similarity_score_threshold = "similarity_score_threshold"
    mmr = "mmr"


@app.command()
def shoot(
    query: str,
    method: SearchMethods = typer.Option("similarity", help="The search method to use"),
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

    results = retriever.get_relevant_documents(query)

    table = utils.create_results_table(results)

    print(table)


class Model(Enum):
    openorca = "openorca"
    orcamini = "orcamini"
    instruct = "instruct"
    falcon = "falcon"

    def to_path(self):
        return {
            "openorca": "models/mistral-7b-openorca.Q4_0.gguf",
            "orcamini": "models/orca-mini-3b-gguf2-q4_0.gguf",
            "instruct": "models/mistral-7b-instruct-v0.1.Q4_0.gguf",
            "falcon": "models/gpt4all-falcon-q4_0.gguf",
        }[self.value]


@app.command()
def fortuneteller(
    question: str,
    threshold: Optional[float] = typer.Option(
        0.3, help="The similarity threshold to use"
    ),
    method: SearchMethods = typer.Option("similarity", help="The search method to use"),
    k: Optional[int] = typer.Option(
        15, help="Number of results to fetch from the vectorstore"
    ),
    model: Model = typer.Option("openorca", help="The model to use for the answer"),
):
    """
    Talk to the fortune teller about your stars
    """

    model_path = model.to_path()

    # error handling for if the model doesn't exist
    if not os.path.exists(model_path):
        raise Exception(
            f"Please download the model {model.value} from https://gpt4all.io/ and place it in {model_path}"
        )

    # IDEA: self-querying:: https://python.langchain.com/docs/modules/data_connection/retrievers/self_query

    chain = RetrievalQA.from_chain_type(
        GPT4All(model=model_path),
        retriever=utils.create_retriever(
            vectorstore_path=VECTORSTORE_PATH,
            k=k,
            method=method.value,
            score_threshold=threshold,
        ),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                input_variables=["context", "question"],
                template="""
    You are an AI assitant with access to my GitHub starred repos. 
    Decide which repos are the relevant repos from {context} to answer the question: 
    {question} and summarise why they are relevant to the topics of the {question}.

    If the repos are not relevant to the question: {question} ignore them. 
    """,
            )
        },
    )

    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task("[cyan]Thinking...", total=100)

        while not progress.finished:
            response = chain.invoke(question)

            progress.update(task, advance=100)

    print(Panel(response.get("result")))

    table = utils.create_results_table(response.get("source_documents"))

    print(table)
