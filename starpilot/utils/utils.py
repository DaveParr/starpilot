import json
import os
import shutil
from typing import Dict, List, Optional

from github import Github, UnknownObjectException
from github.Repository import Repository
from langchain.document_loaders import (JSONLoader, UnstructuredMarkdownLoader,
                                        UnstructuredRSTLoader)
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rich.progress import track

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


def get_user_starred_repos(
    user: str, g: Github, num_repos: Optional[int] = None
) -> List[Repository]:
    starred_repos = []
    for repo in track(
        g.get_user(user).get_starred(), description="Spotting the stars..."
    ):
        starred_repos.append(repo)

    # IDEA: there could be a threshold for star count below which repos are removed
    starred_repos.sort(key=lambda repo: repo.stargazers_count, reverse=True)

    if num_repos is not None:
        starred_repos = starred_repos[:num_repos]

    return starred_repos


def get_repo_contents(
    repos: List[Repository], include_readmes: bool, g: Github
) -> List[Dict]:
    repo_contents = []
    for repo in track(repos, description="Reading the stars..."):
        content = {}
        content["name"] = repo.name
        content["url"] = repo.html_url

        if (description := repo.description) is not None:
            content["description"] = description

        if not (topics := repo.get_topics()) == []:
            content["topics"] = topics

        if include_readmes:
            content["readme"] = {}
            try:
                readme = repo.get_contents("README.md")
                content["readme"]["type"] = "md"
                content["readme"]["content"] = readme.decoded_content.decode("utf-8")
            except UnknownObjectException:
                try:
                    readme = repo.get_contents("README.rst")
                    content["readme"]["type"] = "rst"
                    content["readme"]["content"] = readme.decoded_content.decode(
                        "utf-8"
                    )
                except UnknownObjectException:
                    continue

        repo_contents.append(content)

    return repo_contents


def save_repo_contents_to_disk(
    repo_contents: List[Dict], repo_contents_dir: str = "./repo_content"
) -> None:
    if not os.path.exists(repo_contents_dir):
        os.makedirs(repo_contents_dir)
    else:
        shutil.rmtree(repo_contents_dir)
        os.makedirs(repo_contents_dir)

    for repo in track(repo_contents, description="Mapping the stars..."):
        if set(repo.keys()) == {"name", "url"}:
            # This is a repo with no useful content, so we can skip it
            continue
        else:
            try:
                repo_name = repo["name"]
                repo_write_path = os.path.join(repo_contents_dir, repo_name + ".json")
                with open(repo_write_path, "w") as f:
                    json.dump(repo, f)
            except Exception as e:
                raise Exception(f"Failed to write repo {repo_name} to disk: {e}")


def prepare_topic_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    # Never run, probably broken
    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    documents = []
    for file_path in track(file_paths, description="Loading topics..."):
        loaded_document = JSONLoader(file_path, jq_schema=".topics", text_content=False)
        # only extend the document list if page_content is not ''
        if loaded_document.load()[0].page_content != "":
            documents.extend(loaded_document.load())

    return documents


def prepare_description_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    documents = []
    for file_path in track(file_paths, description="Loading descriptions..."):
        loaded_document = JSONLoader(file_path, jq_schema=".description")
        # only extend the document list if page_content is not ''
        if loaded_document.load()[0].page_content != "":
            documents.extend(loaded_document.load())

    return documents


def prepare_readme_documents(
    repo_contents_dir: str = "./repo_content",
    repo_readmes_dir: str = "./repo_readmes",
) -> List[Document]:
    # IDEA: Use llm to extract the value proposition from the READMEs, then use that as the content for the vectorstore
    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    if not os.path.exists(repo_readmes_dir):
        os.makedirs(repo_readmes_dir)
    else:
        shutil.rmtree(repo_readmes_dir)
        os.makedirs(repo_readmes_dir)

    # TODO: This should enhance the document with url metadata
    documents = []
    for file_path in track(file_paths, description="Loading READMEs..."):
        with open(file_path, "r") as f:
            repo_content = json.load(f)
            repo_name = repo_content["name"]
            if repo_content["readme"] is not None:
                if repo_content["readme"]["type"] == "md":
                    # write MD to file
                    with open(
                        os.path.join(repo_readmes_dir, f"{repo_name}.md"), "w"
                    ) as f:
                        f.write(repo_content["readme"]["content"])
                    loaded_document = UnstructuredMarkdownLoader(
                        repo_readmes_dir + f"/{repo_name}.md",
                    )

                    documents.extend(loaded_document.load())
                elif repo_content["readme"]["type"] == "rst":
                    # write RST to file
                    with open(
                        os.path.join(repo_readmes_dir, f"{repo_name}.rst"), "w"
                    ) as f:
                        f.write(repo_content["readme"]["content"])
                    loaded_document = UnstructuredRSTLoader(
                        repo_readmes_dir + f"/{repo_name}.rst"
                    )
                    documents.extend(
                        loaded_document.load()
                    )  # This needs an install of Pandoc on the system
                else:
                    print(f"Repo {repo_name} readme failed to load")
                    continue

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    splits = text_splitter.split_documents(documents)

    return splits
