###############################################################
# pytest -v --capture=no  tests/test_nfs.py
# npytest -v --capture=no  tests/test_nfs.py::Test_nfs.test_umount
# pytest -v tests/test_nfs.py
###############################################################
import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
import pytest


def run(command):
    parameter = command.split(" ")
    shell_command = parameter[0]
    args = parameter[1:]
    result = Shell.execute(shell_command, args)
    return str(result)

'''def pytest_addoption(parser):
    parser.addoption("--name", action="store", default="default name")

def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    global option_value
    option_value = metafunc.config.option.name
    if 'name' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("name", [option_value])
    print(option_value)
'''
@pytest.mark.incremental
class Test_nfs(object):
    """
    """
    # def test_share(self):
    #     command = 'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red01"'
    #     r = run(command)
    #     print(r)

    def test_help(self):
        command = 'cms help pi'
        r = Shell.run(command)
        print(r)
        assert 'nfs' in r

    def test_install(self):
        command = 'cms pi nfs install'
        r = Shell.run(command)
        print(r)
        assert True

    def test_failed_share(self):
        command = 'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red01,red02,red03"'
        r = Shell.run(command)
        print(r)
        #fails because nonexistent directory
        assert False

    def test_share(self):
        command = 'mkdir Stuff'
        r = Shell.run(command)
        print(r)
        command = 'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red01,red02,red03"'
        r = Shell.run(command)
        print(r)
        assert True

class Rest:

    def test_unshare(self):
        command = 'cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red01"'
        command = 'ls -lisa -h'
        r = run(command)
        print(type(r))
        assert True


