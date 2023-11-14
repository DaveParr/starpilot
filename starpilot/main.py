import typer
from typing_extensions import Optional
from github import Github
import starpilot.utils.utils as utils
import dotenv
import os
from rich import print
from langchain import hub
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema.runnable import RunnablePassthrough
from langchain.llms import GPT4All
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
import shutil

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
    num_repos: Optional[int] = typer.Option(
        None, help="Number of repositories to load"
    ),
) -> None:
    """
    Read the stars

    Read a GitHub user's starred repositories and store the READMEs in a vectorstore
    """

    readme_path = "./readmes"

    if os.path.exists(readme_path):
        shutil.rmtree(readme_path)

    print("Spotting your stars...")

    user_stars = utils.get_user_stars(
        user=user,
        g=GITHUB_CONNECTION,
        num_repos=num_repos,
    )

    repo_contents = utils.get_repo_contents(
        repos=user_stars,
        g=GITHUB_CONNECTION,
    )

    print(f"Reading {len(repo_contents)} stars...")

    print(repo_contents[0])

    utils.save_readmes_to_disk(repo_contents)

    # readme_splits = utils.prepare_github_readmes(path=readme_path)

    # vectorstore_path = "./vectorstore-chroma"

    # if os.path.exists(vectorstore_path):
    #     shutil.rmtree(vectorstore_path)

    # Chroma.from_documents(
    #     documents=readme_splits,
    #     embedding=GPT4AllEmbeddings(disallowed_special=()),
    #     persist_directory="./vectorstore-chroma",
    # )  # IDEA: Set the collection to be the user's name, then only rebuild the vector store for that user, and allow the user to search a different users stars without a rebuild


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
def horoscope(question: str):
    from langchain.chains import RetrievalQA

    retriever = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    ).as_retriever(
        search_type="mmr",
        search_kwargs={"fetch_k": 3},
    )

    model_path = "./models/mistral-7b-openorca.Q4_0.gguf"

    # Callbacks support token-wise streaming
    callbacks = [StreamingStdOutCallbackHandler()]

    # Verbose is required to pass to the callback manager
    llm = GPT4All(model=model_path, verbose=True)

    with_sources_chain = RetrievalQA.from_chain_type(
        llm, retriever=retriever, return_source_documents=True
    )

    response = with_sources_chain.invoke(question)

    print(response["result"])

    for source in response["source_documents"]:
        print(source)
