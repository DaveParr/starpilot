## Starpilot is like copilot, but for GitHub stars.

I've been starring repos for years thinking "This will definitely be useful later".

However I never really went back to them. 

Starpilot is a retrival augmented generation CLI tool for rediscovering your GitHub stars. 

Starpilot helps this problem by allowing you to rediscover GitHub repos you had previously starred that are relevant to your current project.

[Here's some more details about the motivation for and state of the project](https://dev.to/daveparr/copilot-for-your-github-stars-1cep).


### Installation

[![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)

> This project is in early development and is not yet available on PyPi

1. Fork repo
1. Clone repo
1. `cd starpilot`
1. `poetry install`

You will need to have a .env file with
- a [GitHub personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) saved to a `.env` file in the root of the project. 
- a [OpenAI API key](https://platform.openai.com/api-keys) saved to a `.env` file in the root of the project.

```
GITHUB_API_KEY="ghp_..."
OPENAI_API_KEY="sk-..."
```

You will also need to have downloaded `models/mistral-7b-openorca.Q4_0.gguf` from [GPT4All](https://gpt4all.io/index.html), or an [alternative supported by the `Model` class](https://github.com/DaveParr/starpilot/blob/main/starpilot/main.py#L144) and included it in the `models` directory.


You will also potentially need [Pandoc installed](https://pandoc.org/installing.html) on your computer if your starred repos contain a `rst` formatted Readme that you want to load into the database which is used by some Python projects. 

### Usage

[![asciicast](https://asciinema.org/a/622351.svg)](https://asciinema.org/a/622351)

``` bash
starpilot --help
❯ starpilot --help
                                                                                                            
 Usage: starpilot [OPTIONS] COMMAND [ARGS]...                                                               
                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                  │
│ --show-completion             Show completion for the current shell, to copy it or customize the         │
│                               installation.                                                              │
│ --help                        Show this message and exit.                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ astrologer         Use SelfQueryRetriever to self-query the vectorstore                                  │
│ read               Read stars from GitHub                                                                │
│ shoot              Shoot a query at the stars                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯


```