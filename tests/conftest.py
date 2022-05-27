import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="pi")
    parser.addoption("--hostname", action="store", default="red")



@pytest.fixture
def username(request):
    return request.config.getoption("--username")


@pytest.fixture
def hostname(request):
    return request.config.getoption("--hostname")