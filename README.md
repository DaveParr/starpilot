## Starpilot is like copilot, but for GitHub stars.

I've been starring repos for years thinking "This will definitely be useful later".

However I never really went back to them. 

> Starpilot helps this problem by allowing you to rediscover GitHub repos you had previously starred that are relevant to your current project. 

> Starpilot is a retrieval augmented generation CLI tool for rediscovering your GitHub stars. 

> Starpilot uses Large Language Models to query your GitHub stars and return the most relevant repos to your query.


```sh
❯ starpilot astrologer "How can I orchestrate llms?"
                                                   Source Documents                                                    
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repo      ┃ Description             ┃ URL                      ┃ Topic                   ┃ Language                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Flowise   │ Drag & drop UI to build │ https://github.com/Flow… │ artificial-intelligence │ TypeScript JavaScript    │
│           │ your customized LLM     │                          │ chatgpt                 │ CSS SCSS HTML Dockerfile │
│           │ flow                    │                          │ large-language-models   │ Shell Batchfile          │
│           │                         │                          │ llm low-code no-code    │                          │
│           │                         │                          │ hacktoberfest           │                          │
│ langchain │ ⚡ Building             │ https://github.com/lang… │                         │ Python Jupyter Notebook  │
│           │ applications with LLMs  │                          │                         │ MDX Shell Makefile XSLT  │
│           │ through composability   │                          │                         │ HTML Dockerfile TeX      │
│           │ ⚡                      │                          │                         │ JavaScript               │
│ motorhead │ 🧠 Motorhead is a       │ https://github.com/getm… │ machine-learning ml     │ Rust Dockerfile          │
│           │ memory and information  │                          │ mlops rust llmops llms  │                          │
│           │ retrieval server for    │                          │                         │                          │
│           │ LLMs.                   │                          │                         │                          │
│ lancedb   │ Developer-friendly,     │ https://github.com/lanc… │ embeddings llms         │ Python Rust TypeScript   │
│           │ serverless vector       │                          │ vector-search           │ JavaScript Shell         │
│           │ database for AI         │                          │                         │ Dockerfile PowerShell    │
│           │ applications. Easily    │                          │                         │                          │
│           │ add long-term memory to │                          │                         │                          │
│           │ your LLM apps!          │                          │                         │                          │
└───────────┴─────────────────────────┴──────────────────────────┴─────────────────────────┴──────────────────────────┘
```

[Here's some more details about the motivation for and state of the project](https://dev.to/daveparr/copilot-for-your-github-stars-1cep).

[Here is a talk I gave about the project](https://daveparr.quarto.pub/starpilot/)

### Installation

[![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)

> This project is in early development and is not yet available on PyPi

To install the latest version from GitHub run:

``` bash
pip install git+https://github.com/DaveParr/starpilot --user
```
To install the latest tagged release (potentially the more stable approach) from GitHub run:

``` bash
pip install git+https://github.com/DaveParr/starpilot.git@v0.1.4 --user
```


### Setup
You will need to have a .env file with
- a [GitHub personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) saved to a `.env` file in the root of the project. This should have the user> read:user scope permission.
- a [OpenAI API key](https://platform.openai.com/api-keys) saved to a `.env` file in the root of the project. This is needed for Self Query in the `astrologer` command, not semantic similarity via the `shoot` command.

```
GITHUB_API_KEY="ghp_..."
OPENAI_API_KEY="sk-..."
```

The command `starpilot setup` will help you set this up.

#### Optional

This not required for the CLI to work, but is required if `read` is set to include the `README.MD` content for each repo.

You may potentially need [Pandoc installed](https://pandoc.org/installing.html) on your computer if your starred repos contain a `rst` formatted Readme that you want to load into the database which is used by some Python projects. 

### Usage

### `shoot` for simple semantic search

[![asciicast](https://asciinema.org/a/661841.svg)](https://asciinema.org/a/661841)

### `astrologer` for more complex self querying

[![asciicast](https://asciinema.org/a/UvFTn7EMZoUVC8eMbWU59mNyc.svg)](https://asciinema.org/a/UvFTn7EMZoUVC8eMbWU59mNyc)

### Commands

```sh
❯ starpilot --help
                                                                                                                              
 Usage: starpilot [OPTIONS] COMMAND [ARGS]...                                                                                 
                                                                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                    │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.             │
│ --help                        Show this message and exit.                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ astrologer   A self-query of the vectorstore that allows the user to search for a repo while filtering by attributes       │
│ read         Read stars from GitHub                                                                                        │
│ setup        Setup the CLI with the required API keys                                                                      │
│ shoot        An embedding search of the vectorstore                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### More examples

```sh
❯ starpilot astrologer "How do I use dataframes?"
                                                                               Source Documents                                                                                
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Repo       ┃ Description                ┃ URL                                      ┃ Topic                     ┃ Primary Language ┃ Languages                  ┃ Star Count ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ data.table │ R's data.table package     │ https://github.com/Rdatatable/data.table │                           │ R                │ R C Batchfile Shell        │ 3451       │
│            │ extends data.frame:        │                                          │                           │                  │ Makefile C++ CSS           │            │
│            │                            │                                          │                           │                  │ Dockerfile                 │            │
│ tibble     │ A modern re-imagining of   │ https://github.com/tidyverse/tibble      │ r tidy-data               │ R                │ R C Mermaid                │ 641        │
│            │ the data frame             │                                          │                           │                  │                            │            │
│ pandas     │ Flexible and powerful data │ https://github.com/pandas-dev/pandas     │ data-analysis pandas      │ Python           │ Python Shell HTML C Smarty │ 41377      │
│            │ analysis / manipulation    │                                          │ flexible alignment python │                  │ CSS Dockerfile XSLT Cython │            │
│            │ library for Python,        │                                          │ data-science              │                  │ Meson                      │            │
│            │ providing labeled data     │                                          │                           │                  │                            │            │
│            │ structures similar to R    │                                          │                           │                  │                            │            │
│            │ data.frame objects,        │                                          │                           │                  │                            │            │
│            │ statistical functions, and │                                          │                           │                  │                            │            │
│            │ much more                  │                                          │                           │                  │                            │            │
└────────────┴────────────────────────────┴──────────────────────────────────────────┴───────────────────────────┴──────────────────┴────────────────────────────┴────────────┘
```

```sh
❯ starpilot astrologer "How do I use dataframes in Rust?"
                                                                               Source Documents                                                                                
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Repo      ┃ Description                 ┃ URL                                    ┃ Topic                      ┃ Primary Language ┃ Languages                   ┃ Star Count ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ polars    │ Dataframes powered by a     │ https://github.com/pola-rs/polars      │ dataframe-library          │ Rust             │ Rust Python Makefile R CSS  │ 24592      │
│           │ multithreaded, vectorized   │                                        │ dataframe dataframes rust  │                  │                             │            │
│           │ query engine, written in    │                                        │ arrow python out-of-core   │                  │                             │            │
│           │ Rust                        │                                        │ polars                     │                  │                             │            │
│ weld      │ High-performance runtime    │ https://github.com/weld-project/weld   │ stanford data analytics    │ Rust             │ Rust Makefile C++ Python C  │ 2980       │
│           │ for data analytics          │                                        │ machine-learning           │                  │ Shell Batchfile             │            │
│           │ applications                │                                        │ code-generation            │                  │                             │            │
│           │                             │                                        │ performance rust llvm      │                  │                             │            │
│           │                             │                                        │ pandas                     │                  │                             │            │
│ polars-ai │ 💬 Chat with your Polars    │ https://github.com/wiseaidev/polars-ai │ cli dataframe evcxr        │ Rust             │ Rust                        │ 3          │
│           │ DataFrame from your CLI and │                                        │ jupyter openai polars rust │                  │                             │            │
│           │ your app! (WIP)             │                                        │ polars-ai                  │                  │                             │            │
└───────────┴─────────────────────────────┴────────────────────────────────────────┴────────────────────────────┴──────────────────┴─────────────────────────────┴────────────┘
```

```sh
❯ starpilot astrologer "Suggest dataframe packages on CRAN"
                                                                               Source Documents                                                                                
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Repo       ┃ Description                       ┃ URL                                      ┃ Topic       ┃ Primary Language ┃ Languages                         ┃ Star Count ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ tibble     │ A modern re-imagining of the data │ https://github.com/tidyverse/tibble      │ r tidy-data │ R                │ R C Mermaid                       │ 641        │
│            │ frame                             │                                          │             │                  │                                   │            │
│ data.table │ R's data.table package extends    │ https://github.com/Rdatatable/data.table │             │ R                │ R C Batchfile Shell Makefile C++  │ 3451       │
│            │ data.frame:                       │                                          │             │                  │ CSS Dockerfile                    │            │
│ broom      │ Convert statistical analysis      │ https://github.com/dgrtwo/broom          │             │ R                │ R                                 │ 19         │
│            │ objects from R into tidy format   │                                          │             │                  │                                   │            │
└────────────┴───────────────────────────────────┴──────────────────────────────────────────┴─────────────┴──────────────────┴───────────────────────────────────┴────────────┘
```

``` sh
❯ starpilot astrologer "test api python"
                                                                               Source Documents                                                                                
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Repo      ┃ Description                 ┃ URL                                    ┃ Topic                      ┃ Primary Language ┃ Languages                   ┃ Star Count ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ responses │ A utility for mocking out   │ https://github.com/getsentry/responses │ tag-production             │ Python           │ Makefile Python Shell       │ 4018       │
│           │ the Python Requests         │                                        │                            │                  │                             │            │
│           │ library.                    │                                        │                            │                  │                             │            │
│ pytest    │ The pytest framework makes  │ https://github.com/pytest-dev/pytest   │ unit-testing test testing  │ Python           │ Python Gherkin              │ 11164      │
│           │ it easy to write small      │                                        │ python hacktoberfest       │                  │                             │            │
│           │ tests, yet scales to        │                                        │                            │                  │                             │            │
│           │ support complex functional  │                                        │                            │                  │                             │            │
│           │ testing                     │                                        │                            │                  │                             │            │
│ pokeapi   │ The Pokémon API             │ https://github.com/PokeAPI/pokeapi     │ beginner-friendly api      │ Python           │ Python Makefile Dockerfile  │ 3881       │
│           │                             │                                        │ pokemon pokeapi graphql    │                  │ Shell JavaScript Go         │            │
│           │                             │                                        │ hacktoberfest              │                  │                             │            │
└───────────┴─────────────────────────────┴────────────────────────────────────────┴────────────────────────────┴──────────────────┴─────────────────────────────┴────────────┘
```

```sh
❯ starpilot astrologer "How do I manipulate dates and times in R?"
                                                                               Source Documents                                                                                
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃                ┃                ┃                                                                         ┃                 ┃ Primary        ┃                 ┃            ┃
┃ Repo           ┃ Description    ┃ URL                                                                     ┃ Topic           ┃ Language       ┃ Languages       ┃ Star Count ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ lubridate      │ Make working   │ https://github.com/tidyverse/lubridate                                  │ r date-time     │ R              │ Emacs Lisp R    │ 712        │
│                │ with dates in  │                                                                         │ date            │                │ TeX C Shell CSS │            │
│                │ R just that    │                                                                         │                 │                │ Makefile        │            │
│                │ little bit     │                                                                         │                 │                │                 │            │
│                │ easier         │                                                                         │                 │                │                 │            │
│ Hands-On-Time… │ Hands-On-Time… │ https://github.com/PacktPublishing/Hands-On-Time-Series-Analysis-with-R │                 │ R              │ R               │ 102        │
│ fable          │ Tidy time      │ https://github.com/tidyverts/fable                                      │ forecasting     │ R              │ R C++ C         │ 539        │
│                │ series         │                                                                         │                 │                │                 │            │
│                │ forecasting    │                                                                         │                 │                │                 │            │
└────────────────┴────────────────┴─────────────────────────────────────────────────────────────────────────┴─────────────────┴────────────────┴─────────────────┴────────────┘
```