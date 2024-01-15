import pytest

from starpilot.utils.utils import format_repo, prepare_documents

from langchain.schema.document import Document


@pytest.fixture(scope="session")
def pytest_repo():
    return {
        "name": "pytest",
        "nameWithOwner": "pytest-dev/pytest",
        "owner": {"login": "pytest-dev"},
        "url": "https://github.com/pytest-dev/pytest",
        "homepageUrl": "https://pytest.org/",
        "description": "The pytest framework makes it easy to write small tests, yet scales to support complex functional testing",
        "repositoryTopics": {
            "nodes": [
                {"topic": {"name": "unit-testing"}},
                {"topic": {"name": "test"}},
                {"topic": {"name": "testing"}},
                {"topic": {"name": "python"}},
                {"topic": {"name": "hacktoberfest"}},
            ]
        },
        "stargazerCount": 10980,
        "primaryLanguage": {"name": "Python"},
        "languages": {"nodes": [{"name": "Python"}, {"name": "Gherkin"}]},
        "READMEmd": None,
        "READMErst": {
            "text": ".. image:: https://github.com/pytest-dev/pytest/raw/main/doc/en/img/pytest_logo_curves.svg\n   :target: https://docs.pytest.org/en/stable/\n   :align: center\n   :height: 200\n   :alt: pytest\n\n\n------\n\n.. image:: https://img.shields.io/pypi/v/pytest.svg\n    :target: https://pypi.org/project/pytest/\n\n.. image:: https://img.shields.io/conda/vn/conda-forge/pytest.svg\n    :target: https://anaconda.org/conda-forge/pytest\n\n.. image:: https://img.shields.io/pypi/pyversions/pytest.svg\n    :target: https://pypi.org/project/pytest/\n\n.. image:: https://codecov.io/gh/pytest-dev/pytest/branch/main/graph/badge.svg\n    :target: https://codecov.io/gh/pytest-dev/pytest\n    :alt: Code coverage Status\n\n.. image:: https://github.com/pytest-dev/pytest/actions/workflows/test.yml/badge.svg\n    :target: https://github.com/pytest-dev/pytest/actions?query=workflow%3Atest\n\n.. image:: https://results.pre-commit.ci/badge/github/pytest-dev/pytest/main.svg\n   :target: https://results.pre-commit.ci/latest/github/pytest-dev/pytest/main\n   :alt: pre-commit.ci status\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\n.. image:: https://www.codetriage.com/pytest-dev/pytest/badges/users.svg\n    :target: https://www.codetriage.com/pytest-dev/pytest\n\n.. image:: https://readthedocs.org/projects/pytest/badge/?version=latest\n    :target: https://pytest.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://img.shields.io/badge/Discord-pytest--dev-blue\n    :target: https://discord.com/invite/pytest-dev\n    :alt: Discord\n\n.. image:: https://img.shields.io/badge/Libera%20chat-%23pytest-orange\n    :target: https://web.libera.chat/#pytest\n    :alt: Libera chat\n\n\nThe ``pytest`` framework makes it easy to write small tests, yet\nscales to support complex functional testing for applications and libraries.\n\nAn example of a simple test:\n\n.. code-block:: python\n\n    # content of test_sample.py\n    def inc(x):\n        return x + 1\n\n\n    def test_answer():\n        assert inc(3) == 5\n\n\nTo execute it::\n\n    $ pytest\n    ============================= test session starts =============================\n    collected 1 items\n\n    test_sample.py F\n\n    ================================== FAILURES ===================================\n    _________________________________ test_answer _________________________________\n\n        def test_answer():\n    >       assert inc(3) == 5\n    E       assert 4 == 5\n    E        +  where 4 = inc(3)\n\n    test_sample.py:5: AssertionError\n    ========================== 1 failed in 0.04 seconds ===========================\n\n\nDue to ``pytest``'s detailed assertion introspection, only plain ``assert`` statements are used. See `getting-started <https://docs.pytest.org/en/stable/getting-started.html#our-first-test-run>`_ for more examples.\n\n\nFeatures\n--------\n\n- Detailed info on failing `assert statements <https://docs.pytest.org/en/stable/how-to/assert.html>`_ (no need to remember ``self.assert*`` names)\n\n- `Auto-discovery\n  <https://docs.pytest.org/en/stable/explanation/goodpractices.html#python-test-discovery>`_\n  of test modules and functions\n\n- `Modular fixtures <https://docs.pytest.org/en/stable/explanation/fixtures.html>`_ for\n  managing small or parametrized long-lived test resources\n\n- Can run `unittest <https://docs.pytest.org/en/stable/how-to/unittest.html>`_ (or trial)\n  test suites out of the box\n\n- Python 3.8+ or PyPy3\n\n- Rich plugin architecture, with over 850+ `external plugins <https://docs.pytest.org/en/latest/reference/plugin_list.html>`_ and thriving community\n\n\nDocumentation\n-------------\n\nFor full documentation, including installation, tutorials and PDF documents, please see https://docs.pytest.org/en/stable/.\n\n\nBugs/Requests\n-------------\n\nPlease use the `GitHub issue tracker <https://github.com/pytest-dev/pytest/issues>`_ to submit bugs or request features.\n\n\nChangelog\n---------\n\nConsult the `Changelog <https://docs.pytest.org/en/stable/changelog.html>`__ page for fixes and enhancements of each version.\n\n\nSupport pytest\n--------------\n\n`Open Collective`_ is an online funding platform for open and transparent communities.\nIt provides tools to raise money and share your finances in full transparency.\n\nIt is the platform of choice for individuals and companies that want to make one-time or\nmonthly donations directly to the project.\n\nSee more details in the `pytest collective`_.\n\n.. _Open Collective: https://opencollective.com\n.. _pytest collective: https://opencollective.com/pytest\n\n\npytest for enterprise\n---------------------\n\nAvailable as part of the Tidelift Subscription.\n\nThe maintainers of pytest and thousands of other packages are working with Tidelift to deliver commercial support and\nmaintenance for the open source dependencies you use to build your applications.\nSave time, reduce risk, and improve code health, while paying the maintainers of the exact dependencies you use.\n\n`Learn more. <https://tidelift.com/subscription/pkg/pypi-pytest?utm_source=pypi-pytest&utm_medium=referral&utm_campaign=enterprise&utm_term=repo>`_\n\nSecurity\n^^^^^^^^\n\npytest has never been associated with a security vulnerability, but in any case, to report a\nsecurity vulnerability please use the `Tidelift security contact <https://tidelift.com/security>`_.\nTidelift will coordinate the fix and disclosure.\n\n\nLicense\n-------\n\nCopyright Holger Krekel and others, 2004.\n\nDistributed under the terms of the `MIT`_ license, pytest is free and open source software.\n\n.. _`MIT`: https://github.com/pytest-dev/pytest/blob/main/LICENSE\n"
        },
    }


@pytest.fixture(scope="session")
def pytest_expectation(pytest_repo):
    return {
        "name": "pytest",
        "nameWithOwner": "pytest-dev/pytest",
        "owner": "pytest-dev",
        "url": "https://github.com/pytest-dev/pytest",
        "homepageUrl": "https://pytest.org/",
        "description": "The pytest framework makes it easy to write small tests, yet scales to support complex functional testing",
        "topics": [
            "unit-testing",
            "test",
            "testing",
            "python",
            "hacktoberfest",
        ],
        "stargazerCount": 10980,
        "primaryLanguage": "Python",
        "languages": ["Python", "Gherkin"],
        "readme": pytest_repo["READMErst"]["text"],
    }


@pytest.fixture
def calcat_repo():
    return {
        "name": "CalCAT",
        "nameWithOwner": "StateOfCalifornia/CalCAT",
        "owner": {"login": "StateOfCalifornia"},
        "url": "https://github.com/StateOfCalifornia/CalCAT",
        "homepageUrl": "",
        "description": "California Communicable diseases Assessment Tool",
        "repositoryTopics": {"nodes": []},
        "stargazerCount": 219,
        "primaryLanguage": {"name": "R"},
        "languages": {
            "nodes": [{"name": "R"}, {"name": "CSS"}, {"name": "JavaScript"}]
        },
        "READMEmd": {
            "text": "![](www/calcat_long.png)\n# Introduction \nWelcome to the California Communicable diseases Assessment Tool (CalCAT).  This repository contains an application written in Shiny and for use with any US state to assist in assessing the many different models available for understanding COVID-19 transmission and spread. It brings together several data sources that are publicly available, and can be supplemented with your own data to improve the assessment. \n\n# Getting Started \n_ATTN: This application is designed to run with Rstudio. If you need to download and install Rstudio go [here](https://rstudio.com/) to get started._ \n\n0. __Fork this Repository__\n1. Enter your state's name in line 50 of the `cal_cat_data_routine.rmd` where it says ```state_name <- \"California\"```\n``Ctrl+Alt+R``\nThis routine will download data for your state from a number of different modeling groups. You can find out more about them in the Technical notes app the application. \n2. You may also modify the data path for the application (line 59), but it defaults to a subdirectory named for your state, for example `data/CA`. \n3. Each data source feeding the CalCAT has one or more functions in the `R` folder which pull the data down when the RMarkdown file is run. You can run this daily to ensure your app has the freshest data. \n4. Once the data routine markdown has completed, you can follow the output messages to see if any sources returned errors. If so, please [submit an issue](https://github.com/StateOfCalifornia/CalCAT/issues) letting us know what problem you ran into. \n5. Next, you can run the app by opening the `global.R` file and again modifying the state name, now on line 39 (for example `state_name <- \"Arizona\"`).\n6. Run and deploy the app. \n\n![](www/calcat_ga_screen.png)\n\n# Build and Test\nThe California version of the app, [CalCAT](https://calcat.covid19.ca.gov/cacovidmodels/), brings together even more publicly available data on cases, deaths, hospitalizations, and bed capacity. Many of these data likely exist in your region. You will need to update these inputs for maximal utility. \n\n# Contribute\nWe can't wait to see what you do with this. Please fork, edit and send us back as [pull requests](https://github.com/StateOfCalifornia/CalCAT/pulls) the changes you'd like to see. Maybe you'll incorporate your own estimator of R-Effective, or add functionality to import data; you could improve on our simple ensemble estimates. Go Wild!\n\n__A gift from California with love.__\n_\u201cTogether, all things are possible.\u201d_\n                -- Cesar Chavez \n\n### Resources\n- [CalCAT California Version](http://calcat.covid19.ca.gov)\n- [covid19.ca.gov](https://covid19.ca.gov/)\n"
        },
        "READMErst": None,
    }


@pytest.fixture
def calcat_expectation(calcat_repo):
    return {
        "name": "CalCAT",
        "nameWithOwner": "StateOfCalifornia/CalCAT",
        "owner": "StateOfCalifornia",
        "url": "https://github.com/StateOfCalifornia/CalCAT",
        "description": "California Communicable diseases Assessment Tool",
        "stargazerCount": 219,
        "primaryLanguage": "R",
        "languages": ["R", "CSS", "JavaScript"],
        "readme": calcat_repo["READMEmd"]["text"],
    }


@pytest.fixture
def the_open_book_repo():
    return {
        "name": "The-Open-Book",
        "nameWithOwner": "joeycastillo/The-Open-Book",
        "owner": {"login": "joeycastillo"},
        "url": "https://github.com/joeycastillo/The-Open-Book",
        "homepageUrl": None,
        "description": None,
        "repositoryTopics": {"nodes": []},
        "stargazerCount": 7265,
        "primaryLanguage": None,
        "languages": {"nodes": []},
        "READMEmd": {
            "text": "# The Open Book: Project Reboot\n\n**A note from the project creator:** The Open Book was my first real electronics project; the earliest designs date to late 2019. I have learned a lot since those early days, and as such, here three years later, I am hitting reset. At this time the repository contains a version of the Open Book designed around the Raspberry Pi Pico. It's optimized for low part count and easy hand assembly, but it runs on AAA batteries and may not be as svelte as some folks might prefer. At a later date, I hope to design a followup with built-in LiPo charging and a slimmer profile, but at this time, this version of the book is the quickest path to getting hardware in people's hands so that we can start hacking on firmware together.\n\nFor details on how to build, test and use Open Book, I've [made documentation available here](https://www.oddlyspecificobjects.com/projects/openbook/).\n\nThe original Open Book repository has been archived in a branch called [original](https://github.com/joeycastillo/The-Open-Book/tree/original).\n\n[The Open Book firmware, called libros, is under development here](https://github.com/joeycastillo/libros). It's a goddamn mess in some ways, and in dire need of some documentation, but for the moment it does do the job of presenting a list of books stored on an SD card, and letting you read them. The canonical format for books is plain text with the book title on the first line, OR plain text plus some front matter and some ASCII control codes for chapter breaks and formatting, [as documented here](https://www.oddlyspecificobjects.com/projects/openbook/#advanced-text-formatting).\n\n## Original Introduction\n\nAs a society, we need an open source device for reading. Books are among the most important documents of our culture, yet the most popular and widespread devices we have for reading \u2014 the Kobo, the Nook, the Kindle and even the iPad \u2014 are closed devices, operating as small moving parts in a set of giant closed platforms whose owners' interests are not always aligned with readers'.\n\nThe Open Book aims to be a simple device that anyone with a soldering iron can build for themselves. The Open Book should be comprehensible: the reader should be able to look at it and understand, at least in broad strokes, how it works. It should be extensible, so that a reader with different needs can write code and add accessories that make the book work for them. It should be global, supporting readers of books in all the languages of the world. Most of all, it should be open, so that anyone can take this design as a starting point and use it to build a better book.\n\n## State of the Book\n\nAt this time, the Pi Pico book is in decent shape if you want to try your hand at building it yourself. You will need to have two custom things fabricated: the **Open Book Main Board** (which you can get as a bare PCB) and the **Castellated E-Paper Driver** module (which you'll want to have done as a PCBA job). All the files you will need to send out for this can be found in the **Fabrication Files** folder in the project root:\n\n* Upload `OSO-BOOK-C1-04-rounded.zip` to your PCB fabrication house of choice. It is designed to be a two-layer, 1 mm thick PCB, and you can use either an ENIG or lead-free HASL finish.\n* If you plan to use JLCPCB's economic PCBA service, upload all three files in `OSO-BOOK-C2-01` to JLCPCB. Opt for a 1 mm thick lead-free HASL finish. Note that the board is slightly wider than it needs to be, just to meet the minimum size requirements for this service.\n* If you plan to use PCBWay's PCBA service, upload all three files in `OSO-BOOK-C2-02` to PCBWay. Once again, opt for a 1 mm thick lead-free HASL finish. \n\nOther Parts: \n\n* Two of these [side mount buttons](https://www.digikey.com/en/products/detail/w\u00fcrth-elektronik/434351045816/5209090)\n* One of these [side-mount switches](https://www.digikey.com/en/products/detail/c-k/JS102011SAQN/1640095)\n* One [MEM2075 MicroSD card slot](https://www.digikey.com/en/products/detail/gct/MEM2075-00-140-01-A/9859614)\n* One [GD25Q16C Flash chip](https://www.digikey.com/en/products/detail/gigadevice-semiconductor-hk-limited/GD25Q16CTIGR/9484675) with SOIC / SOP8 footprint.\n* One [Keystone 1022 dual AAA battery holder](https://www.digikey.com/en/products/detail/keystone-electronics/1022/2137859) (you can get clones on Aliexpress for cheap)\n* Two P-channel MOSFETS with SOT23 footprint (I use the DMG3415)\n* Two 10k\u03a9 resistors with 1206 footprint.\n* Two 10\u00b5F capacitors with 1206 footprint (rated voltage >=6.3V).\n* One 1\u00b5F capacitor with 0805 footprint (rated voltage >=6.3V).\n* Seven through-hole slim tactile buttons (3mm by 6mm; [TL1107 type](https://www.digikey.com/en/products/detail/e-switch/TL1107AF130WQ/378976))\n* One [GDEW042T2 grayscale e-paper display](https://buy-lcd.com/products/42inch-e-inkanel-spi-interface-buy-eaper-display). (Don't get the tri-color version; it'll end in heartbreak)\n* And finally, one [Raspberry Pi Pico](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793) board\n\nThe Open Book is open source hardware: you should feel free to build one yourself, order parts for ten and do a workshop at your local maker space, or even buy parts for fifty and sell them as kits. \n\nPlease steal this book.\n\nI plan to add more documentation in the new year, but until then, [this half-hour video walks through building one Open Book board in real-time](https://twitter.com/i/broadcasts/1OyKAVPjrvaGb).\n\n### Forking and tweaking the boards\n\n* Design files for the Open Book main board can be found in the `OSO-BOOK-C1` folder. It's a KiCad project.\n* Design files for the castellated e-paper driver module can be found in the `OSO-BOOK-C2` folder. Alas, they are Eagle projects that predate my move to KiCad. There are two versions: an older version that was successfully fabricated with JLCPCB's economic PCBA service (`OSO-BOOK-C2-01`), and a newer version successfully fabricated using PCBWay's PCBA service (`OSO-BOOK-C2-02`). Both work great.\n\n## License\n\n Different components of the project are licensed differently, see [LICENSE.md](https://github.com/joeycastillo/The-Open-Book/blob/main/LICENSE.md).\n"
        },
        "READMErst": None,
    }


@pytest.fixture
def the_open_book_expectation(the_open_book_repo):
    return {
        "name": "The-Open-Book",
        "nameWithOwner": "joeycastillo/The-Open-Book",
        "owner": "joeycastillo",
        "url": "https://github.com/joeycastillo/The-Open-Book",
        "stargazerCount": 7265,
        "readme": the_open_book_repo["READMEmd"]["text"],
    }


@pytest.fixture
def minimal_repo():
    return {
        "name": "fakerepo",
        "nameWithOwner": "fakeuser/fakerepo",
        "owner": {"login": "fakeuser"},
        "url": "https://github.com/fakeuser/fakerepo",
        "homepageUrl": None,
        "description": None,
        "repositoryTopics": {"nodes": []},
        "stargazerCount": 1,
        "primaryLanguage": None,
        "languages": {"nodes": []},
        "READMEmd": None,
        "READMErst": None,
    }


@pytest.fixture
def minimal_expectation(minimal_repo):
    return {
        "name": "fakerepo",
        "nameWithOwner": "fakeuser/fakerepo",
        "owner": "fakeuser",
        "url": "https://github.com/fakeuser/fakerepo",
        "stargazerCount": 1,
    }


@pytest.fixture
def emoji_metadata_repo():
    return {
        "name": "gh-i",
        "nameWithOwner": "gennaro-tedesco/gh-i",
        "owner": {"login": "gennaro-tedesco"},
        "url": "https://github.com/gennaro-tedesco/gh-i",
        "homepageUrl": None,
        "description": "🔎 search your github issues interactively",
        "repositoryTopics": {
            "nodes": [
                {"topic": {"name": "gh-extension"}},
                {"topic": {"name": "command-line"}},
                {"topic": {"name": "go"}},
            ]
        },
        "stargazerCount": 52,
        "primaryLanguage": {"name": "Go"},
        "languages": {
            "nodes": [
                {"name": "Go"},
            ]
        },
        "READMEmd": None,
        "READMErst": None,
    }


@pytest.fixture
def emoji_metadata_expectation():
    return {
        "name": "gh-i",
        "nameWithOwner": "gennaro-tedesco/gh-i",
        "owner": "gennaro-tedesco",
        "url": "https://github.com/gennaro-tedesco/gh-i",
        "description": "🔎 search your github issues interactively",
        "topics": [
            "gh-extension",
            "command-line",
            "go",
        ],
        "stargazerCount": 52,
        "primaryLanguage": "Go",
        "languages": ["Go"],
    }


repos_and_expectations = [
    ("pytest_repo", "pytest_expectation"),
    ("calcat_repo", "calcat_expectation"),
    ("the_open_book_repo", "the_open_book_expectation"),
    ("minimal_repo", "minimal_expectation"),
    ("emoji_metadata_repo", "emoji_metadata_expectation"),
]


@pytest.mark.parametrize("repo_fixture, expectation_fixture", repos_and_expectations)
def test_format_repo(request, repo_fixture, expectation_fixture):
    repo = request.getfixturevalue(repo_fixture)
    expectation = request.getfixturevalue(expectation_fixture)
    result = format_repo(repo)
    print(result)

    # check each key in expectation is in results
    for key in expectation.keys():
        assert key in result.keys()

    # check each value in expectation is in the right key in results
    for key, value in expectation.items():
        assert result[key] == value

    # check only the keys in expectation are in results
    for key in result.keys():
        assert key in expectation.keys()

    # check no values are None
    for value in result.values():
        assert value is not None

    # check no values are empty strings
    for value in result.values():
        assert value != ""


def test_prepare_document():
    result = prepare_documents("./tests/test_data/")

    assert len(result) == 3

    for document in result:
        assert isinstance(document, Document)

    for document in result:
        assert document.metadata is not None

    for document in result:
        for key, value in document.metadata.items():
            assert value is not None

    for document in result:
        assert document.page_content is not None

    names = [document.metadata["name"] for document in result]

    assert "pytest" in names
    assert "The-Open-Book" in names
    assert "gh-i" in names

    for document in result:
        if document.metadata["name"] == "pytest":
            assert document.metadata["url"] == "https://github.com/pytest-dev/pytest"
            assert (
                document.metadata["topics"]
                == "unit-testing test testing python hacktoberfest"
            )
            assert (
                document.metadata["description"]
                == "The pytest framework makes it easy to write small tests, yet scales to support complex functional testing"
            )
            assert document.metadata["languages"] == "Python Gherkin"
        elif document.metadata["name"] == "The-Open-Book":
            assert (
                document.metadata["url"]
                == "https://github.com/joeycastillo/The-Open-Book"
            )
            assert document.metadata.get("description") is None
            assert document.metadata.get("topics") is None
            assert document.metadata.get("languages") is None
        elif document.metadata["name"] == "gh-i":
            assert (
                document.metadata["url"] == "https: //github.com/gennaro-tedesco/gh-i"
            )
            assert document.metadata["topics"] == "gh-extension command-line go"
            assert (
                document.metadata["description"]
                == "🔎 search your github issues interactively"
            )
            assert document.metadata["languages"] == "Go"
