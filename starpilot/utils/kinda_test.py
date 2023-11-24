import os

import dotenv
import github
import utils
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma

dotenv.load_dotenv()

git_hub_key = os.getenv("GITHUB_API_KEY")

GITHUB_CONNECTION = github.Github(git_hub_key)

# utils.get_user_starred_repos("DaveParr", GITHUB_CONNECTION, num_repos=2)

repo_names = [
    "starship/starship",  # totally fine
    "django/django",  # description and topic but readme is rst
    "StateOfCalifornia/CalCAT",  # description but no topic
    "joeycastillo/The-Open-Book",  # no description or topic
    "vicenews/shot-by-cops",  # no description or topic
    "pytorch/pytorch",  # no owner or organisation
]

repo_list = []

pytorch_repo = GITHUB_CONNECTION.get_repo("pytorch/pytorch")

print(pytorch_repo.organization.name)

print(pytorch_repo.owner.name)


for repo in repo_names:
    repo_content = GITHUB_CONNECTION.get_repo(repo)
    repo_list.append(repo_content)

print(repo_list[0].full_name)

repo_descriptions = []

content = utils.get_repo_contents(repo_list, False, GITHUB_CONNECTION)

utils.save_repo_contents_to_disk(content, "./tmp")

generic_documents = utils.prepare_documents("./tmp")

print(generic_documents)


Chroma.from_documents(
    documents=generic_documents,
    embedding=GPT4AllEmbeddings(disallowed_special=()),
    persist_directory="./tmp",
)


retriever = utils.create_retriever(
    vectorstore_path="./tmp",
    k=2,
    method="similarity",
)

response = retriever.get_relevant_documents("machine learning")

print(response)
