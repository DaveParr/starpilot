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


@app.command()
def shoot(
    query: str,
    similarity: Optional[float] = typer.Option(
        None, help="The similarity threshold to use"
    ),
    k: Optional[int] = typer.Option(
        15, help="Number of results to fetch from the vectorstore"
    ),
):
    """
    Shoot a query at the stars
    """

    if similarity is not None:
        method = "similarity_score_threshold"
        score_threshold = similarity
    else:
        method = "mmr"
        score_threshold = None

    if not os.path.exists(VECTORSTORE_PATH):
        raise Exception("Please load the stars before shooting")

    vectorstore_retrival = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    ).as_retriever(
        search_type=method,
        search_kwargs={
            "k": k,
            "score_threshold": score_threshold,
        },
    )

    results = vectorstore_retrival.get_relevant_documents(query)

    for result in results:
        print(result)


@app.command()
def fortuneteller(
    question: str,
    similarity: Optional[float] = typer.Option(
        None, help="The similarity threshold to use"
    ),
    k: Optional[int] = typer.Option(
        15, help="Number of results to fetch from the vectorstore"
    ),
):
    """
    Talk to the fortune teller about your stars
    """

    model_path = "./models/mistral-7b-openorca.Q4_0.gguf"

    template = """
    You are an AI assitant with access to my GitHub starred repos. 
    Select which repos are the relevant repos from {context} to answer the question: 
    {question} and summarise them.

    If the repos are not relevant to the question ignore them. 
    """

    # IDEA: self-querying:: https://python.langchain.com/docs/modules/data_connection/retrievers/self_query

    if similarity is not None:
        method = "similarity_score_threshold"
        score_threshold = similarity
    else:
        method = "mmr"
        score_threshold = None

    chain = RetrievalQA.from_chain_type(
        GPT4All(model=model_path),
        retriever=Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=GPT4AllEmbeddings(disallowed_special=()),
        ).as_retriever(
            search_type=method,
            search_kwargs={"k": k, "score_threshold": score_threshold},
        ),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                input_variables=["context", "question"], template=template
            )
        },
    )

    response = chain.invoke(question)

    print(response)
