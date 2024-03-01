import json
import os
import shutil
import token
from enum import Enum
from typing import Dict, List, Optional, Tuple

import structlog
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from graphql_query import (
    Argument,
    Field,
    Operation,
    Query,
)
from langchain.schema.document import Document
from langchain.vectorstores.utils import filter_complex_metadata
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from rich.progress import track
from rich.table import Table
from sqlalchemy import over

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

logger = structlog.get_logger(__name__)


def get_user_starred_repos(username: str, github_api_key: str) -> List:
    """
    Get the starred repos for a user using github GraphQL API
    """

    after_cursor = ""
    all_results = []

    def _get_page_of_user_starred_repos(
        user: str,
        github_api_key: str,
        after_cursor: str = "",
    ) -> Tuple[List[Dict], Optional[str]]:
        """
        Get a page of the starred repos for a user using github GraphQL API
        """

        logger.debug("Creating GraphQL query", after_cursor=after_cursor)

        headers = {
            "Authorization": f"Bearer {github_api_key}",
        }

        transport = AIOHTTPTransport(
            url="https://api.github.com/graphql", headers=headers
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        def _construct_user_starred_repos_query(
            username: str, after: str = ""
        ) -> Query:
            """
            Generate a GraphQL query to get the starred repos for a user
            """
            user_starred_repos_query = Query(
                name="user",
                arguments=[Argument(name="login", value=f'"{username}"')],
                fields=[
                    "login",
                    "name",
                    Field(
                        name="starredRepositories",
                        arguments=[
                            Argument(
                                name="first", value=100
                            ),  # 100 is the max accepted
                            Argument(name="after", value=f'"{after}"'),
                        ],
                        fields=[
                            Field(
                                name="edges",
                                fields=[
                                    "cursor",
                                    Field(
                                        name="node",
                                        fields=[
                                            "name",
                                            "nameWithOwner",
                                            Field(
                                                name="owner",
                                                fields=["login"],
                                            ),
                                            "url",
                                            "homepageUrl",
                                            "description",
                                            Field(
                                                name="repositoryTopics",
                                                arguments=[
                                                    Argument(name="first", value=20)
                                                ],
                                                fields=[
                                                    Field(
                                                        name="nodes",
                                                        fields=[
                                                            Field(
                                                                name="topic",
                                                                fields=["name"],
                                                            )
                                                        ],
                                                    )
                                                ],
                                            ),
                                            "stargazerCount",
                                            Field(
                                                name="primaryLanguage",
                                                fields=["name"],
                                            ),
                                            Field(
                                                name="languages",
                                                arguments=[
                                                    Argument(name="first", value=20)
                                                ],
                                                fields=[
                                                    Field(name="nodes", fields=["name"])
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )

            return user_starred_repos_query

        user_starred_repos_query = _construct_user_starred_repos_query(
            user, after_cursor
        )

        operation = Operation(
            type="query",
            name="UserStarredRepos",
            queries=[user_starred_repos_query],
        )

        # this call is sorta flaky, and has failed with timeout errors without ovveriding the timeout default
        # rate limit docs: https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api
        result = client.execute(gql(operation.render()))

        edges = result["user"]["starredRepositories"]["edges"]

        def _get_next_cursor(edges: List[Dict]) -> Optional[str]:
            """
            Get the cursor for the next page of results
            """
            if edges:
                return edges[-1]["cursor"]
            else:
                return None

        next_cursor = _get_next_cursor(edges)

        repos: List[Dict] = [edge["node"] for edge in edges]

        return repos, next_cursor

    while True:
        print(f"Fetching page of starred repos for {username}")
        result, after_cursor = _get_page_of_user_starred_repos(
            user=username, github_api_key=github_api_key, after_cursor=after_cursor
        )

        all_results.append(result)

        if after_cursor is None:
            print("No more pages of results")
            break

    all_results = [item for sublist in all_results for item in sublist]

    logger.info("User starred repos", user=username, number_of_repos=len(all_results))

    return all_results


def format_repo(repo: Dict) -> Dict:
    """
    Format the repos into a list of dicts with values suitable for ingesting into the vectorstore
    """

    formatted_repo = {
        "name": repo["name"],
        "nameWithOwner": repo["nameWithOwner"],
        "url": repo["url"],
        "homepageUrl": repo["homepageUrl"],
        "description": repo["description"],
        "stargazerCount": repo["stargazerCount"],
        "primaryLanguage": repo["primaryLanguage"]["name"]
        if repo["primaryLanguage"]
        else None,
        "languages": [language["name"] for language in repo["languages"]["nodes"]],
        "owner": repo["owner"]["login"],
        "topics": [
            topic["topic"]["name"] for topic in repo["repositoryTopics"]["nodes"]
        ],
        # join name, description, topics if they are not none
        "content": " ".join(
            filter(
                None,
                [
                    repo["name"],
                    repo["description"],
                    " ".join(
                        [
                            topic["topic"]["name"]
                            for topic in repo["repositoryTopics"]["nodes"]
                        ]
                    ),
                    repo["primaryLanguage"]["name"]
                    if repo["primaryLanguage"]
                    else None,
                ],
            )
        ),
    }

    # remove keys with None, empty values, or empty strings
    for key, value in list(formatted_repo.items()):
        if value in [None, [], ""]:
            logger.debug("Dropped missing value", key=key, repo=repo["name"])
            del formatted_repo[key]

    return formatted_repo


def save_repo_contents_to_disk(
    repo_contents: List[Dict], repo_contents_dir: str = "./repo_content"
) -> None:
    """
    Save the repo contents to disk
    """
    if not os.path.exists(repo_contents_dir):
        os.makedirs(repo_contents_dir)
    else:
        shutil.rmtree(repo_contents_dir)
        os.makedirs(repo_contents_dir)

    for repo in track(repo_contents, description="Mapping the stars..."):
        repo_name = repo["name"]
        try:
            repo_write_path = os.path.join(repo_contents_dir, repo_name + ".json")
            with open(repo_write_path, "w") as file:
                json.dump(repo, file)
        except Exception as exception:
            raise Exception(f"Failed to write repo {repo_name} to disk") from exception


def prepare_documents(
    repo_contents_dir: str = "./repo_content",
) -> List[Document]:
    """
    Prepare the documents for ingestion into the vectorstore
    """
    import tiktoken

    file_paths = []
    for file in os.listdir(repo_contents_dir):
        file_paths.append(os.path.join(repo_contents_dir, file))

    def _metadata_func(record: dict, metadata: dict) -> dict:
        metadata["url"] = record.get("url")
        metadata["name"] = record.get("name")
        metadata["stargazerCount"] = record["stargazerCount"]
        if (primary_language := record.get("primaryLanguage")) is not None:
            metadata["primaryLanguage"] = primary_language
        if (description := record.get("description")) is not None:
            metadata["description"] = description
        if (topics := record.get("topics")) is not None:
            metadata["topics"] = " ".join(topics)
        if (languages := record.get("languages")) is not None:
            metadata["languages"] = " ".join(languages)
        # TODO: Add starcount to metadata

        # if any of the fields are not one of (str, bool, int, float) log a warning
        for key, value in metadata.items():
            if not isinstance(value, (str, bool, int, float)):
                logger.warning(
                    "Metadata value is not one of (str, bool, int, float)",
                    key=key,
                    value=value,
                    type=type(value),
                    repo=record.get("name"),
                )

        return metadata

    documents = []
    for file_path in track(file_paths, description="Loading documents..."):
        logger.debug("Loading document", file=file_path)
        loader = JSONLoader(
            file_path,
            jq_schema=".",  # FIXME: This drops the other fields from metadata
            content_key="content",
            metadata_func=_metadata_func,
            text_content=False,
        )
        if (loaded_document := loader.load())[0].page_content != "":
            documents.extend(loaded_document)

    def _num_tokens_from_string(string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    # calculate the sum total tokens for the content of each document

    token_lengths = []
    for document in documents:
        token_lengths.append(
            _num_tokens_from_string(document.page_content, "cl100k_base")
        )

    price_per_million_tokens = 0.13

    logger.info(
        "Token lengths",
        total_tokens=sum(token_lengths),
        mean_tokens=sum(token_lengths) / len(token_lengths),
        total_cost=sum(token_lengths) * price_per_million_tokens / 1e6,
    )

    documents = filter_complex_metadata(documents)

    return documents


class SearchMethods(Enum):
    """
    Enum for the different search methods
    """

    similarity = "similarity"
    similarity_score_threshold = "similarity_score_threshold"
    mmr = "mmr"


def create_retriever(
    vectorstore_path: str,
    k: int,
    method: SearchMethods = SearchMethods.similarity,
):
    """
    Create a retriever from a vectorstore
    """
    return Chroma(
        persist_directory=vectorstore_path,
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-large"
        ),  # FIXME: This will break if openai embedding # type:ignore  # Tried to find a way to suppress the model card from being printed, failed: https://github.com/langchain-ai/langchain/discussions/13663 # type: ignore
    ).as_retriever(
        search_type=method,
        search_kwargs={
            "k": k,
        },
    )


def create_results_table(response: List[Document]) -> Table:
    """
    Create a rich table from the response
    """
    table = Table(title="Source Documents")

    table.add_column("Repo")  # TODO: make this text a link to the repo
    table.add_column("Description")
    table.add_column(
        "URL", no_wrap=True
    )  # This is so the link is always clickable, truncated text in this cilumn truncates the link
    table.add_column("Topic")
    table.add_column("Primary Language")
    table.add_column("Languages")
    table.add_column("Star Count")

    for source_document in response:
        table.add_row(
            source_document.metadata.get("name"),
            source_document.metadata.get("description"),
            source_document.metadata.get("url"),
            source_document.metadata.get("topics"),
            source_document.metadata.get("primaryLanguage"),
            source_document.metadata.get("languages"),
            str(source_document.metadata.get("stargazerCount")),
        )

    return table
