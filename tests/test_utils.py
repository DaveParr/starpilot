from unittest.mock import Mock

import pytest

from starpilot.utils.utils import get_repo_contents, get_user_starred_repos


def test_get_user_starred_repos_mocked():
    # Mock the necessary objects
    class MockRepo:
        def __init__(self, stargazers_count):
            self.stargazers_count = stargazers_count

    class MockUser:
        def get_starred(self):
            return [MockRepo(10), MockRepo(5), MockRepo(8), MockRepo(3), MockRepo(7)]

    class MockGithub:
        def get_user(self, user):
            return MockUser()

    # Call the function under test
    result = get_user_starred_repos("testuser", MockGithub(), num_repos=3)

    # Assert the expected result
    assert len(result) == 3
    assert result[0].stargazers_count == 10
    assert result[1].stargazers_count == 8
    assert result[2].stargazers_count == 7


@pytest.mark.vcr()
def test_get_user_starred_repos_vcr():
    import os

    import github

    github_client = github.Github(os.getenv("GITHUB_API_KEY"))

    result = get_user_starred_repos("DaveParr", github_client, num_repos=3)

    assert len(result) == 3
    assert isinstance(result[0], github.Repository.Repository)


def test_get_repo_contents_with_readmes():
    # Mock the necessary objects
    class MockRepo:
        def __init__(
            self,
            full_name,
            name,
            html_url,
            owner,
            organization,
            description,
            topics,
            languages,
        ):
            self.full_name = full_name
            self.name = name
            self.html_url = html_url
            self.owner = owner
            self.organization = organization
            self.description = description
            self.topics = topics
            self.languages = languages

        def get_languages(self):
            return self.languages

        def get_topics(self):
            return self.topics

        def get_contents(self, path):
            if path == "README.md":
                return Mock(decoded_content=b"Mock README content")
            elif path == "README.rst":
                return Mock(decoded_content=b"Mock README content")
            else:
                raise UnknownObjectException

    class MockGithub:
        def __init__(self, repos):
            self.repos = repos

        def get_repo(self, full_name):
            for repo in self.repos:
                if repo.full_name == full_name:
                    return repo

    # Create mock repositories
    repos = [
        MockRepo(
            "user/repo1",
            "repo1",
            "https://github.com/user/repo1",
            Mock(name="owner"),
            Mock(name="organization"),
            "Repo 1 description",
            ["topic1", "topic2"],
            ["Python", "JavaScript"],
        ),
        MockRepo(
            "user/repo2",
            "repo2",
            "https://github.com/user/repo2",
            Mock(name="owner"),
            None,
            "Repo 2 description",
            [],
            ["Python"],
        ),
        MockRepo(
            "user/repo3",
            "repo3",
            "https://github.com/user/repo3",
            Mock(name="owner"),
            Mock(name="organization"),
            None,
            ["topic1"],
            [],
        ),
    ]

    # Mock the Github client
    github_client = MockGithub(repos)

    # Call the function under test
    result = get_repo_contents(repos, github_client, include_readmes=True)

    # Assert the expected result
    assert len(result) == 2

    assert result[0]["id"] == "user/repo1"
    assert result[0]["name"] == "repo1"
    assert result[0]["url"] == "https://github.com/user/repo1"
    assert "owner" in result[0]
