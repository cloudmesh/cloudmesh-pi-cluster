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

    def setup(self):
        pass

    def test_umount(self):
        HEADING()
        command = 'cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red01"'
        r = run(command)
        ignore, result = r.split('GGGG')
        print('Ignore: ', ignore)
        print('Result: ', result)
        result = eval(result)
        print(ignore)
        print('gggg',type(result),result)
        assert False
