import os
from cProfile import Profile

import dotenv
import github
import utils
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from rich import print

dotenv.load_dotenv()

profile = Profile()
profile.enable()
git_hub_key = os.getenv("GITHUB_API_KEY")

GITHUB_CONNECTION = github.Github(git_hub_key)

# utils.get_user_starred_repos("DaveParr", GITHUB_CONNECTION, num_repos=2)

repo_names = [
    "starship/starship",  # totally fine
    "DaveParr/starpilot",
    "django/django",  # description and topic but readme is rst
    "StateOfCalifornia/CalCAT",  # description but no topic
    "joeycastillo/The-Open-Book",  # no description or topic or language
    "vicenews/shot-by-cops",  # no description or topic
    "pytorch/pytorch",  # no owner or organisation
]

repo_list = []

for repo in repo_names:
    repo_content = GITHUB_CONNECTION.get_repo(repo)
    repo_list.append(repo_content)


content = utils.format_repos(repo_list, GITHUB_CONNECTION, False)

print(content)

# utils.save_repo_contents_to_disk(content, "./tmp")

# generic_documents = utils.prepare_documents("./tmp")


# Chroma.from_documents(
#     documents=generic_documents,
#     embedding=GPT4AllEmbeddings(disallowed_special=()),
#     persist_directory="./tmp",
# )


# retriever = utils.create_retriever(
#     vectorstore_path="./tmp",
#     k=2,
#     method="similarity",
# )

# response = retriever.get_relevant_documents("starship/starship")

# print(utils.create_results_table(response))

profile.disable()

profile.dump_stats("for.pstats")
