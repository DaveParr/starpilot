import pytest
import pytest_vcr

from starpilot.utils.utils import get_user_starred_repos


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
