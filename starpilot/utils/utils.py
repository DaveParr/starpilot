from typing import List
import os
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from github.Repository import Repository
from github import Github, UnknownObjectException
from langchain.schema.document import Document


def get_user_stars(user: str, g: Github) -> List[Repository]:
    starred_repos = []
    for repo in g.get_user(user).get_starred():
        starred_repos.append(repo)
    return starred_repos


def get_repo_descriptions(repos: List[Repository], g: Github) -> List[Repository]:
    descriptions = []
    for repo in repos:
        description = repo.description
        if description is not None:
            descriptions.append(description)
    return descriptions


def get_repo_readmes(repos: List[Repository], g: Github) -> List[Repository]:
    readmes = []
    for repo in repos:
        try:
            readme = repo.get_contents("README.md")
        except UnknownObjectException:
            try:
                readme = repo.get_contents("README.rst")
            except UnknownObjectException:
                readme = None
        if readme is not None:
            readmes.append(readme.decoded_content.decode("utf-8"))
    return readmes


def save_readmes_to_disk(
    readmes: List[Repository], repos: List[Repository], directory: str = "./readmes"
) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in range(len(readmes)):
        with open(f"{directory}/{repos[i].name}.md", "w") as f:
            # FIXME: This assumes the list of readmes and repos are in the same order and the same length
            # In fact django-allauth is labelled proton-ge-custom and analogsea is labelled sinew
            # IDEA: Treat `RST` with more care
            f.write(readmes[i])


def prepare_github_readmes(path: str) -> List[Document]:
    # IDEA: This could be refactored into a DocumentLoader. If it is then it would read files sequentially, and then ditch them to keep only 1 in memory at once.
    file_paths = []
    for file in os.listdir(path):
        file_paths.append(os.path.join(path, file))

    documents = []
    for file_path in file_paths:
        loader = UnstructuredMarkdownLoader(file_path)
        # IDEA: modify behaviour for RST vs MD: https://api.python.langchain.com/en/latest/document_loaders/langchain.document_loaders.rst.UnstructuredRSTLoader.html
        documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    splits = text_splitter.split_documents(documents)

    return splits
