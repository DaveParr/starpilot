import json
import os
import shutil
from enum import Enum
from typing import Dict, List, Optional

import structlog
from github import Github, UnknownObjectException
from github.Repository import Repository
from langchain.document_loaders import (JSONLoader, UnstructuredMarkdownLoader,
                                        UnstructuredRSTLoader)
from langchain.embeddings import GPT4AllEmbeddings
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from rich.progress import track
from rich.table import Table

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

logger = structlog.get_logger(__name__)


def _metadata_func(record: dict, metadata: dict) -> dict:
    metadata["url"] = record["url"]
    metadata["name"] = record["name"]
    metadata["owner"] = record["owner"]
    return metadata


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
    repo_infos = []
    for repo in track(repos, description="Reading the stars..."):
        repo_info = {}
        repo_slug = repo.full_name
        repo_info["id"] = repo_slug
        repo_info["name"] = repo.name
        repo_info["url"] = repo.html_url

        if (owner := repo.owner.name) is not None:
            repo_info["owner"] = owner

        if (repo.organization) is not None:
            if (organization := repo.organization.name) is not None:
                repo_info["organization"] = organization
            else:
                logger.info("No organization name", repo=repo_slug)

        # get the repo languages
        repo_info["languages"] = []
        for language in repo.get_languages():
            repo_info["languages"].append(language)

        if len(repo_info["languages"]) == 0:
            logger.info("No languages", repo=repo_slug)

        if (description := repo.description) is not None:
            repo_info["description"] = description
        else:
            logger.info("No description", repo=repo_slug)

        if not (topics := repo.get_topics()) == []:
            repo_info["topics"] = topics

        if include_readmes:
            repo_info["readme"] = {}
            try:
                readme = repo.get_contents("README.md")
                repo_info["readme"]["type"] = "md"
                repo_info["readme"]["content"] = readme.decoded_content.decode("utf-8")
            except UnknownObjectException:
                try:
                    readme = repo.get_contents("README.rst")
                    repo_info["readme"]["type"] = "rst"
                    repo_info["readme"]["content"] = readme.decoded_content.decode(
                        "utf-8"
                    )
                except UnknownObjectException:
                    continue

        repo_info["vectorstore_document"] = []

        if repo_info.get("description"):
            repo_info["vectorstore_document"].append(
                {
                    "content": repo_info.get("description"),
                    "url": repo_info.get("url"),
                    "name": repo_info.get("name"),
                    "topics": repo_info.get("topics"),
                    "languages": repo_info.get("languages"),
                }
            )

            repo_infos.append(repo_info)
            logger.debug("Using repo", repo=repo_slug)
        else:
            logger.warning("Repo has no relevant information to use", repo=repo_slug)

    return repo_infos


def save_repo_contents_to_disk(
    repo_contents: List[Dict], repo_contents_dir: str = "./repo_content"
) -> None:
    if not os.path.exists(repo_contents_dir):
        os.makedirs(repo_contents_dir)
    else:
        shutil.rmtree(repo_contents_dir)
        os.makedirs(repo_contents_dir)

    for repo in track(repo_contents, description="Mapping the stars..."):
        try:
            repo_name = repo["name"]
            repo_write_path = os.path.join(repo_contents_dir, repo_name + ".json")
            with open(repo_write_path, "w") as f:
                json.dump(repo, f)
        except Exception as e:
            raise Exception(f"Failed to write repo {repo_name} to disk: {e}")


def prepare_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    def _metadata_func_new(record: dict, metadata: dict) -> dict:
        metadata["url"] = record.get("url")
        metadata["name"] = record.get("name")

        if (topics := record.get("topics")) is not None:
            metadata["topics"] = " ".join(topics)
        if (languages := record.get("languages")) is not None:
            metadata["languages"] = " ".join(languages)
        return metadata

    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    documents = []
    for file_path in track(file_paths, description="Loading documents..."):
        logger.debug("Loading document", file=file_path)
        loader = JSONLoader(
            file_path,
            jq_schema=".vectorstore_document[]",
            content_key="content",
            metadata_func=_metadata_func_new,
            text_content=False,
        )
        if (loaded := loader.load())[
            0
        ].page_content != "":  # only extend the document list if page_content is not ''
            documents.extend(loaded)

    return documents


def prepare_topic_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    documents = []
    for file_path in track(file_paths, description="Loading topics..."):
        loader = JSONLoader(
            file_path,
            jq_schema=".",
            content_key="topics",
            metadata_func=_metadata_func,
            text_content=False,
        )
        if (loaded := loader.load())[
            0
        ].page_content != "":  # only extend the document list if page_content is not ''
            documents.extend(loaded)

    return documents


def prepare_description_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    documents = []
    for file_path in track(file_paths, description="Loading descriptions..."):
        loader = JSONLoader(
            file_path,
            jq_schema=".",
            content_key="description",
            metadata_func=_metadata_func,
        )
        if (loaded := loader.load())[
            0
        ].page_content != "":  # only extend the document list if page_content is not ''
            documents.extend(loaded)

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


class SearchMethods(Enum):
    similarity = "similarity"
    similarity_score_threshold = "similarity_score_threshold"
    mmr = "mmr"


def create_retriever(
    vectorstore_path: str,
    k: int,
    method: SearchMethods = "similarity",
    score_threshold: float = 0.3,
):
    """
    Create a retriever from a vectorstore

    Args:
        vectorstore_path (str): The path to the vectorstore
        k (int): The number of results to return
        method (str): The search method to use
        score_threshold (float): The similarity threshold to use
    """
    return Chroma(
        persist_directory=vectorstore_path,
        embedding_function=GPT4AllEmbeddings(),  # Tried to find a way to suppress the model card from being printed, failed: https://github.com/langchain-ai/langchain/discussions/13663
    ).as_retriever(
        search_type=method,
        search_kwargs={
            "k": k,
            "score_threshold": score_threshold,
        },
    )


def create_results_table(response: dict) -> Table:
    table = Table(title="Source Documents")

    table.add_column("Document")
    table.add_column("Repo")
    table.add_column("URL")
    table.add_column("Topic")

    for source_document in response:
        table.add_row(
            source_document.page_content,
            source_document.metadata.get("name"),
            source_document.metadata.get("url"),
            source_document.metadata.get("topics"),
        )

    return table
