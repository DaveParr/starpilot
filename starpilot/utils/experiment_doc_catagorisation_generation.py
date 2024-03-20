import json
import os
from typing import List

import tiktoken
from icecream import ic

dir = "./repo_content/"
docs: dict = {}

# List all files in the directory using os.listdir
for filename in os.listdir(dir):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Open the file
        with open(os.path.join(dir, filename), "r") as f:
            # Load the JSON data from the file
            data = json.load(f)
            # Use the filename (without extension) as the key and the data as the value
            docs[os.path.splitext(filename)[0]] = data

print(len(docs))

# filter top 100 by stars
top_repos = sorted(docs.items(), key=lambda x: x[1]["stargazerCount"], reverse=True)[
    :100
]

ic(top_repos[0])


# count tokens in sorted docs using tiktokens


def _num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    ic(string)
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


top_repos_content = [repo[1] for repo in top_repos]

# get the number of tokens for each 'content' value in each repo descprition
ic(top_repos_content)


total_tokens = []
# for repo in top_100_repos extract the content and count the tokens
for repo in top_repos_content:
    total_tokens.append(_num_tokens_from_string(repo["content"], "cl100k_base"))

print(sum(total_tokens))

import langchain
import langchain_community
import langchain_openai
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAI

llm = OpenAI()
instruction_text = "Suggest 5 catagories to classify these github code repositories into. The catagories should be short and descriptive, such as 'Web App', or 'Data Science'."

repos: List[str] = [repo["content"] for repo in top_repos_content]

repos_string = ""
# Join the list into a single string with a dictionary-like structure
for repo in top_repos_content:
    repo_string = f'{{"name": "{repo["name"]}", "content": "{repo["content"]}"}},'
    repos_string += repo_string

response_text = "Do not use the '/' character in your catagory names. Format your response as a python dict. The key should be the catagory name, the value should be 3 example repositories that fit into that catagory from the information above. For example: {'Web App': ['repo1', 'repo2', 'repo3']}"


message = instruction_text + repos_string + response_text

# messages = [HumanMessage(content=message)]

# response_1 = llm.invoke(messages)

# ic(response_1)

# response_2 = llm.invoke(messages)

# ic(response_2)

# use json_parser to format the response into a dict https://python.langchain.com/docs/modules/model_io/output_parsers/types/json

from typing import List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

model = ChatOpenAI(temperature=0)


class Catagory(BaseModel):
    name: str = Field(description="The name of the catagory")
    repos: List[str] = Field(
        description="The names of the repositories that fit into this catagory"
    )


class CatagoryResponse(BaseModel):
    catagories: List[Catagory] = Field(
        description="The catagories and the repositories that fit into them"
    )


parser = JsonOutputParser(pydantic_object=CatagoryResponse)

prompt = PromptTemplate(
    template="""Suggest {num_catagories} catagories to classify these github code repositories into. 
    The catagories should be short and descriptive, such as 'Web App', or 'Data Science'. 
    {repos}
    {format_instructions}""",
    input_variables=["repos", "num_catagories"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser

response = chain.invoke({"repos": repos_string, "num_catagories": 10})

ic(response)
