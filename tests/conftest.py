def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="default name")
    parser.addoption("--hostname", action="store", default="default user")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.name
    if 'username' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("username", [option_value])
    if 'hostname' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("hostname", [option_value])
