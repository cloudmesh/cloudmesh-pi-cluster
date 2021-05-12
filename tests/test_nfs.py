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


@pytest.mark.incremental
class Test_nfs(object):
    """
    """
    def test_share(self):
        command = 'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red01"'
        r = run(command)
        print(r)
        

    def test_unshare(self):
        command = 'cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red01"'
        r = run(command)
        print(r)
        assert True
