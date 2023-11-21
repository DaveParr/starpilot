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

You will also need to have downloaded `models/mistral-7b-openorca.Q4_0.gguf` from [GPT4All](https://gpt4all.io/index.html), or an [alternative supported by the `Model` class](https://github.com/DaveParr/starpilot/blob/main/starpilot/main.py#L144) and included it in the `models` directory.


You will also potentially need [Pandoc installed](https://pandoc.org/installing.html) on your computer if your starred repos contain a `rst` formatted Readme that you want to load into the database. 

### Usage

[![asciicast](https://asciinema.org/a/622351.svg)](https://asciinema.org/a/622351)

``` bash
starpilot --help
```