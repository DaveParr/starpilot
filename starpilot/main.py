import typer
from github import Github
import starpilot.utils.utils as utils
import dotenv
import os
from rich import print
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
import shutil
from typing_extensions import Optional

app = typer.Typer()

dotenv.load_dotenv()

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

    print("Reading your stars...")

    user_stars = utils.get_user_stars(user, GITHUB_CONNECTION)

    user_stars.sort(key=lambda repo: repo.stargazers_count, reverse=True)

    user_stars = user_stars[:num_repos] if num_repos is not None else user_stars

    repo_readmes = utils.get_repo_readmes(user_stars, GITHUB_CONNECTION)

    utils.save_readmes_to_disk(repo_readmes, user_stars)

    readme_splits = utils.prepare_github_readmes(path=readme_path)

    vectorstore_path = "./vectorstore-chroma"

    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    print("Mapping your stars...")

    Chroma.from_documents(
        documents=readme_splits,
        embedding=GPT4AllEmbeddings(disallowed_special=()),
        persist_directory="./vectorstore-chroma",
    )


@app.command()
def shoot(query: str):
    """
    Shoot the stars

    Shoot your stars to discover the most similar READMEs
    """

    vectorstore_path = "./vectorstore-chroma"

    if not os.path.exists(vectorstore_path):
        raise Exception("Please load the stars before shooting")

    vectorstore_retrival = Chroma(
        persist_directory="./vectorstore-chroma",
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    )

    results = vectorstore_retrival.similarity_search(query)

    for result in results:
        print(result)
