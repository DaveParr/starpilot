import pytest
from langchain.schema.document import Document

from starpilot.utils.utils import format_repo, prepare_documents


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
        "content": "pytest The pytest framework makes it easy to write small tests, yet scales to support complex functional testing unit-testing test testing python hacktoberfest Python",
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
        "content": "CalCAT California Communicable diseases Assessment Tool R",
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
    }


@pytest.fixture
def the_open_book_expectation(the_open_book_repo):
    return {
        "name": "The-Open-Book",
        "nameWithOwner": "joeycastillo/The-Open-Book",
        "owner": "joeycastillo",
        "url": "https://github.com/joeycastillo/The-Open-Book",
        "stargazerCount": 7265,
        "content": "The-Open-Book",
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
    }


@pytest.fixture
def minimal_expectation(minimal_repo):
    return {
        "name": "fakerepo",
        "nameWithOwner": "fakeuser/fakerepo",
        "owner": "fakeuser",
        "url": "https://github.com/fakeuser/fakerepo",
        "stargazerCount": 1,
        "content": "fakerepo",
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
        "content": "gh-i 🔎 search your github issues interactively gh-extension command-line go Go",
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
            assert document.metadata["url"] == "https://github.com/gennaro-tedesco/gh-i"
            assert document.metadata["topics"] == "gh-extension command-line go"
            assert (
                document.metadata["description"]
                == "🔎 search your github issues interactively "
            )
            assert document.metadata["languages"] == "Go"
