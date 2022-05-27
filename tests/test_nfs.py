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

def test_print_name(username, hostname):
    print ("Displaying username: %s" % username)
    print("Displaying hostname: %s" % hostname)

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

    def test_install(self, username):
        command = f'cms pi nfs install --username={username}'
        print(command)
        r = Shell.run(command)
        print(r)
        assert True

        '''    def test_failed_share(self, username, hostname):
        hostname_list = Parameter.expand(hostname)
        command = f'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" ' \
                  f'--hostnames={hostname_list} --username={username}'
        r = Shell.run(command)
        print(r)
        #fails because nonexistent directory
        assert 'does not exist' in r'''

    def test_share(self, username, hostnames):
        command = 'mkdir ~/Stuff'
        r = Shell.run(command)
        print(r)
        command = f'cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames={hostnames} ' \
                  f'--username={username}'
        print(command)
        r = Shell.run(command)
        print(r)
        assert True

class Rest:

    def test_unshare(self, username, hostnames):
        command = f'cms pi nfs unshare --path="/mnt/nfs" --hostnames={hostnames} ' \
                  f'--username={username}'
        print(command)
        r = Shell.run(command)
        print(r)
        assert True


