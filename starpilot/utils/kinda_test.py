import github
import dotenv
import os
import utils

dotenv.load_dotenv()

git_hub_key = os.getenv("GITHUB_API_KEY")

GITHUB_CONNECTION = github.Github(git_hub_key)

# utils.get_user_starred_repos("DaveParr", GITHUB_CONNECTION, num_repos=2)

repo_names = [
    "starship/starship",  # totally fine
    "joeycastillo/The-Open-Book",  # no description or topic
    "vicenews/shot-by-cops",  # no description or topic
    "StateOfCalifornia/CalCAT",  # description but no topic
]

repo_list = []
for repo in repo_names:
    repo_content = GITHUB_CONNECTION.get_repo(repo)
    repo_list.append(repo_content)

repo_descriptions = []

content = utils.get_repo_contents(repo_list, False, GITHUB_CONNECTION)

utils.save_repo_contents_to_disk(content, "./tmp")

description_documents = utils.prepare_description_documents("./tmp")

print(description_documents)

topic_documents = utils.prepare_topic_documents("./tmp")

print(topic_documents)
