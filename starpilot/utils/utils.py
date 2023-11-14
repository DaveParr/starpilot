from typing import List, Optional, Dict
import os
import json
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from github.Repository import Repository
from github import Github, UnknownObjectException
from langchain.schema.document import Document


def get_user_stars(
    user: str, g: Github, num_repos: Optional[int] = None
) -> List[Repository]:
    starred_repos = []
    for repo in g.get_user(user).get_starred():
        starred_repos.append(repo)

    # IDEAS: there could be a threshold for star count below which repos are removed
    starred_repos.sort(key=lambda repo: repo.stargazers_count, reverse=True)

    if num_repos is not None:
        starred_repos = starred_repos[:num_repos]

    return starred_repos


def get_repo_contents(repos: List[Repository], g: Github) -> List[Dict]:
    repo_contents = []
    for repo in repos:
        content = {}
        content["name"] = repo.name
        content["url"] = repo.html_url
        content["description"] = repo.description
        content["topics"] = repo.get_topics()
        content["readme"] = {}
        try:
            readme = repo.get_contents("README.md")
            content["readme"]["type"] = "md"
            content["readme"]["content"] = readme.decoded_content.decode("utf-8")
        except UnknownObjectException:
            try:
                readme = repo.get_contents("README.rst")
                content["readme"]["type"] = "rst"
                content["readme"]["content"] = readme.decoded_content.decode("utf-8")
            except UnknownObjectException:
                content["readme"]["type"] = None
                content["readme"] = None
        repo_contents.append(content)
    return repo_contents


def save_repo_contents_to_disk(
    repo_contents: List[Dict], directory: str = "./repo_content"
) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)
    for repo in repo_contents:
        with open(os.path.join(directory, repo["name"] + ".json"), "w") as f:
            json.dump(repo, f)


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
