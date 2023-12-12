## Starpilot is like copilot, but for GitHub stars.

I've been starring repos for years thinking "This will definitely be useful later".

However I never really went back to them. 

> Starpilot helps this problem by allowing you to rediscover GitHub repos you had previously starred that are relevant to your current project. 

> Starpilot is a retrival augmented generation CLI tool for rediscovering your GitHub stars. 

> Starpilot uses Large Lanugage Models to query your GitHub stars and return the most relevant repos to your query.


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

### Installation

[![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)

> This project is in early development and is not yet available on PyPi

To install the latest version from GitHub run:

``` bash
pip install git+https://github.com/DaveParr/starpilot --user
```
To install the latest tagged release (potentially the more stable approach) from GitHub run:

``` bash
pip install git+https://github.com/DaveParr/starpilot.git@v.0.1.0 --user
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

[![asciicast](https://asciinema.org/a/626456.svg)](https://asciinema.org/a/626456)

### Commands

``` bash
❯ starpilot --help
                                                                                                                 
 Usage: starpilot [OPTIONS] COMMAND [ARGS]...                                                                    
                                                                                                                 
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                       │
│ --show-completion             Show completion for the current shell, to copy it or customize the              │
│                               installation.                                                                   │
│ --help                        Show this message and exit.                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ astrologer          Use SelfQueryRetriever to self-query the vectorstore                                      │
│ read                Read stars from GitHub                                                                    │
│ setup               Setup the CLI with the required API keys                                                  │
│ shoot               Shoot a query at the stars                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### More examples

```sh
❯ starpilot astrologer "How do I use dataframes?"
                                                   Source Documents                                                    
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repo    ┃ Description              ┃ URL                      ┃ Topic                    ┃ Language                 ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pandas  │ Flexible and powerful    │ https://github.com/pand… │ data-analysis pandas     │ Python Cython HTML C     │
│         │ data analysis /          │                          │ flexible alignment       │ Shell Meson Smarty CSS   │
│         │ manipulation library for │                          │ python data-science      │ Dockerfile XSLT          │
│         │ Python, providing        │                          │                          │                          │
│         │ labeled data structures  │                          │                          │                          │
│         │ similar to R data.frame  │                          │                          │                          │
│         │ objects, statistical     │                          │                          │                          │
│         │ functions, and much more │                          │                          │                          │
│ polars  │ Dataframes powered by a  │ https://github.com/pola… │ dataframe-library        │ Rust Python Makefile R   │
│         │ multithreaded,           │                          │ dataframe dataframes     │ CSS                      │
│         │ vectorized query engine, │                          │ rust arrow python        │                          │
│         │ written in Rust          │                          │ out-of-core polars       │                          │
│ pandera │ A light-weight,          │ https://github.com/unio… │ pandas validation schema │ Python Makefile          │
│         │ flexible, and expressive │                          │ dataframes testing       │                          │
│         │ statistical data testing │                          │ pandas-validation        │                          │
│         │ library                  │                          │ pandas-dataframe         │                          │
│         │                          │                          │ data-validation          │                          │
│         │                          │                          │ data-cleaning data-check │                          │
│         │                          │                          │ testing-tools assertions │                          │
│         │                          │                          │ data-assertions          │                          │
│         │                          │                          │ data-verification        │                          │
│         │                          │                          │ dataframe-schema         │                          │
│         │                          │                          │ hypothesis-testing       │                          │
│         │                          │                          │ pandas-validator         │                          │
│         │                          │                          │ data-processing          │                          │
│ koalas  │ Koalas: pandas API on    │ https://github.com/data… │ spark pandas pydata      │ Python Shell             │
│         │ Apache Spark             │                          │ dataframe mlflow         │                          │
│         │                          │                          │ big-data data-science    │                          │
└─────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘

```

```sh
❯ starpilot astrologer "How do I use dataframes in Rust?"
                                                   Source Documents                                                    
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repo   ┃ Description              ┃ URL                      ┃ Topic                     ┃ Language                 ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ polars │ Dataframes powered by a  │ https://github.com/pola… │ dataframe-library         │ Rust Python Makefile R   │
│        │ multithreaded,           │                          │ dataframe dataframes rust │ CSS                      │
│        │ vectorized query engine, │                          │ arrow python out-of-core  │                          │
│        │ written in Rust          │                          │ polars                    │                          │
│ lance  │ Modern columnar data     │ https://github.com/lanc… │ machine-learning          │ Rust Python Jupyter      │
│        │ format for ML and LLMs   │                          │ computer-vision           │ Notebook C Shell CMake   │
│        │ implemented in Rust.     │                          │ data-format deep-learning │ C++ Makefile Dockerfile  │
│        │ Convert from parquet in  │                          │ python apache-arrow       │                          │
│        │ 2 lines of code for 100x │                          │ duckdb mlops              │                          │
│        │ faster random access,    │                          │ data-analysis             │                          │
│        │ vector index, and data   │                          │ data-analytics            │                          │
│        │ versioning. Compatible   │                          │ data-science dataops      │                          │
│        │ with Pandas, DuckDB,     │                          │ data-centric embeddings   │                          │
│        │ Polars, Pyarrow, with    │                          │ rust llms                 │                          │
│        │ more integrations        │                          │                           │                          │
│        │ coming..                 │                          │                           │                          │
│ linfa  │ A Rust machine learning  │ https://github.com/rust… │ machine-learning rust     │ Rust Python Gnuplot      │
│        │ framework.               │                          │ algorithms                │                          │
│        │                          │                          │ scientific-computing      │                          │
│ burn   │ Burn is a new            │ https://github.com/trac… │ autodiff deep-learning    │ Rust WGSL Python Shell   │
│        │ comprehensive dynamic    │                          │ machine-learning rust     │ PowerShell               │
│        │ Deep Learning Framework  │                          │ scientific-computing      │                          │
│        │ built using Rust with    │                          │ ndarray tensor            │                          │
│        │ extreme flexibility,     │                          │ neural-network pytorch    │                          │
│        │ compute efficiency and   │                          │ autotune concurrency      │                          │
│        │ portability as its       │                          │ cross-platform            │                          │
│        │ primary goals.           │                          │ high-performance          │                          │
│        │                          │                          │ kernel-fusion llm onnx    │                          │
│        │                          │                          │ wasm webgpu               │                          │
└────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┴──────────────────────────┘

```

```sh
❯ starpilot astrologer "How do I use dataframes with R?"
                                                   Source Documents                                                    
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repo       ┃ Description             ┃ URL                     ┃ Topic                    ┃ Language                ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pandas     │ Flexible and powerful   │ https://github.com/pan… │ data-analysis pandas     │ Python Cython HTML C    │
│            │ data analysis /         │                         │ flexible alignment       │ Shell Meson Smarty CSS  │
│            │ manipulation library    │                         │ python data-science      │ Dockerfile XSLT         │
│            │ for Python, providing   │                         │                          │                         │
│            │ labeled data structures │                         │                          │                         │
│            │ similar to R data.frame │                         │                          │                         │
│            │ objects, statistical    │                         │                          │                         │
│            │ functions, and much     │                         │                          │                         │
│            │ more                    │                         │                          │                         │
│ tibble     │ A modern re-imagining   │ https://github.com/tid… │ r tidy-data              │ R C Mermaid             │
│            │ of the data frame       │                         │                          │                         │
│ ggplot2    │ An implementation of    │ https://github.com/tid… │ r visualisation          │ R                       │
│            │ the Grammar of Graphics │                         │ data-visualisation       │                         │
│            │ in R                    │                         │                          │                         │
│ data.table │ R's data.table package  │ https://github.com/Rda… │                          │ R C Batchfile Shell C++ │
│            │ extends data.frame:     │                         │                          │ Makefile Dockerfile CSS │
└────────────┴─────────────────────────┴─────────────────────────┴──────────────────────────┴─────────────────────────┘

```

``` sh
❯ starpilot astrologer "test api python"
bert_load_from_file: gguf version     = 2
bert_load_from_file: gguf alignment   = 32
bert_load_from_file: gguf data offset = 695552
bert_load_from_file: model name           = BERT
bert_load_from_file: model architecture   = bert
bert_load_from_file: model file type      = 1
bert_load_from_file: bert tokenizer vocab = 30522
                                                   Source Documents                                                    
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repo          ┃ Description             ┃ URL                     ┃ Topic                   ┃ Language              ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ pytest        │ The pytest framework    │ https://github.com/pyt… │ unit-testing test       │ Python Gherkin        │
│               │ makes it easy to write  │                         │ testing python          │                       │
│               │ small tests, yet scales │                         │ hacktoberfest           │                       │
│               │ to support complex      │                         │                         │                       │
│               │ functional testing      │                         │                         │                       │
│ responses     │ A utility for mocking   │ https://github.com/get… │ tag-production          │ Python Shell Makefile │
│               │ out the Python Requests │                         │                         │                       │
│               │ library.                │                         │                         │                       │
│ vcrpy         │ Automatically mock your │ https://github.com/kev… │ testing python http     │ Python Shell          │
│               │ HTTP interactions to    │                         │ mocking                 │                       │
│               │ simplify and speed up   │                         │                         │                       │
│               │ testing                 │                         │                         │                       │
│ squidgy-testy │ A unit test framework   │ https://github.com/squ… │                         │ Python                │
│               │ for prompts.            │                         │                         │                       │
└───────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┴───────────────────────┘       
```

```sh
❯ starpilot astrologer "How do I manipulate dates and times in R?"
                                                   Source Documents                                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Repo                     ┃ Description              ┃ URL                      ┃ Topic                   ┃ Language ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ seer                     │ 📈 Feature-based         │ https://github.com/thiy… │                         │ R        │
│                          │ Forecast Model Selection │                          │                         │          │
│                          │ (FFORMS) 🕐 🕜 🕙 🕥 🕚  │                          │                         │          │
│                          │ 🕦 🕛 🕧 🕑 🕝 🕒 🕞 🕓  │                          │                         │          │
│                          │ 🕟 🕔 🕠 🕕 🕡 🕖 🕢 🕗  │                          │                         │          │
│                          │ 🕣 🕘 🕤                 │                          │                         │          │
│ EventsVis                │ A tool for analyzing and │ https://github.com/micr… │ time-series-analysis    │ R        │
│                          │ visualizing discrete     │                          │ visualization r shiny   │          │
│                          │ temporal events          │                          │                         │          │
│ Hands-On-Time-Series-An… │ Hands-On-Time-Series-An… │ https://github.com/Pack… │                         │ R        │
│ CausalImpact             │ An R package for causal  │ https://github.com/goog… │                         │ R        │
│                          │ inference in time series │                          │                         │          │
└──────────────────────────┴──────────────────────────┴──────────────────────────┴─────────────────────────┴──────────┘

```