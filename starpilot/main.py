import typer
from github import Github
import starpilot.utils.utils as utils
import dotenv
import os
from rich import print
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma

app = typer.Typer()

dotenv.load_dotenv()

try:
    git_hub_key = os.getenv("GITHUB_API_KEY")
except Exception:
    raise Exception("Please create a .env file with your GitHub token")

GITHUB_CONNECTION = Github(git_hub_key)


@app.command()
def load():
    """
    Load the stars
    """
    if not os.path.exists("./readmes"):
        user_stars = utils.get_user_stars("DaveParr", GITHUB_CONNECTION)
        repo_descriptions = utils.get_repo_readmes(user_stars, GITHUB_CONNECTION)
        utils.save_readmes_to_disk(repo_descriptions, user_stars)

        readme_splits = utils.prepare_github_readmes(path="./readmes/")

        vectorstore = Chroma.from_documents(
            documents=readme_splits,
            embedding=GPT4AllEmbeddings(disallowed_special=()),
        )

    print(vectorstore.similarity_search("large language models"))


@app.command()
def shoot():
    """
    Shoot the stars
    """

    pass
