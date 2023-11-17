from langchain.chains import RetrievalQA
import typer
from typing_extensions import Optional
from github import Github
import starpilot.utils.utils as utils
import dotenv
import os
from rich import print
import shutil
from langchain.llms import GPT4All
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from icecream import install
from langchain.prompts import PromptTemplate
from enum import Enum


class only_values(str, Enum):
    all = "all"
    descriptions = "descriptions"
    readmes = "readmes"
    topics = "topics"


try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

install()

app = typer.Typer()

dotenv.load_dotenv()

VECTORSTORE_PATH = "./vectorstore-chroma"

try:
    git_hub_key = os.getenv("GITHUB_API_KEY")
except Exception:
    raise Exception("Please create a .env file with your GitHub token")

GITHUB_CONNECTION = Github(git_hub_key)


@app.command()
def read(
    user: str,
    only: Optional[only_values] = typer.Option(
        only_values.all, help="Only read descriptions or readmes"
    ),
    num_repos: Optional[int] = typer.Option(
        None, help="Number of repositories to load"
    ),
) -> None:
    """
    Read the stars

    Read a GitHub user's starred repositories and store the READMEs in a vectorstore
    """
    print("Spotting your stars...")

    repos = utils.get_user_starred_repos(
        user=user,
        g=GITHUB_CONNECTION,
        num_repos=num_repos,
    )

    repo_contents = utils.get_repo_contents(
        repos=repos,
        g=GITHUB_CONNECTION,
    )

    print(f"Reading {len(repo_contents)} stars...")

    utils.save_repo_contents_to_disk(repo_contents=repo_contents)

    vectorstore_path = "./vectorstore-chroma"

    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    # IDEA: Set the collection to be the user's name, then only rebuild the vector store for that user, and allow the user to search a different users stars without a rebuild

    if only == only_values.all or only == only_values.descriptions:
        repo_descriptions = utils.prepare_description_documents()

        Chroma.from_documents(
            documents=repo_descriptions,
            embedding=GPT4AllEmbeddings(disallowed_special=()),
            persist_directory=vectorstore_path,
        )

    if only == only_values.all or only == only_values.topics:
        repo_topics = utils.prepare_topic_documents()

        Chroma.from_documents(
            documents=repo_topics,
            embedding=GPT4AllEmbeddings(disallowed_special=()),
            persist_directory=vectorstore_path,
        )

    if only == only_values.all or only == only_values.readmes:
        readme_documents = utils.prepare_readme_documents()

        Chroma.from_documents(
            documents=readme_documents,
            embedding=GPT4AllEmbeddings(disallowed_special=()),
            persist_directory=vectorstore_path,
        )


@app.command()
def shoot(query: str):
    """
    Shoot the stars

    Shoot your stars to discover the most similar READMEs
    """

    if not os.path.exists(VECTORSTORE_PATH):
        raise Exception("Please load the stars before shooting")

    vectorstore_retrival = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    )

    results = vectorstore_retrival.similarity_search(query)

    for result in results:
        print(result)


@app.command()
def fortuneteller(
    question: str,
    fetch_k: Optional[int] = typer.Option(
        15, help="Number of results to fetch from the vectorstore"
    ),
):
    """
    Talk to the fortune teller

    Ask the fortune teller a question and receive an answer from the stars
    """

    model_path = "./models/mistral-7b-openorca.Q4_0.gguf"

    template = """
    You are an AI assitant with access to a users GitHub starred repos. 
    Here is some information about GitHub repos this user has starred: {context}
    Breifly summarise why these repos are relevant to the question {question}

    If they are not do not use them in your answer. 
    """

    chain = RetrievalQA.from_chain_type(
        GPT4All(model=model_path),
        retriever=Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=GPT4AllEmbeddings(disallowed_special=()),
        ).as_retriever(
            search_type="mmr",
            search_kwargs={"fetch_k": fetch_k},
        ),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                input_variables=["context", "question"], template=template
            )
        },
    )

    response = chain.invoke(question)

    print(response["result"])

    for source in response["source_documents"]:
        print(source)
