from cloudmesh.common.parameter import Parameter
import textwrap

class Mpi:
    """
    pi mpi install [NAMES]
    pi mpirun [--hosts=HOSTS] --parameters=PARAMETERS] COMMAND
    """

    # the install script may have to be modified according to
    # https://thenewstack.io/installing-mpi-python-raspberry-pi-cluster-runs-docker/

    install_script = textwrap.dedent("""
        sudo apt-get install python-mpi4py
        """)


    def __init__(self):
        self.hosts = None
        raise NotImplementedError

    def install(self, names):
        """
        installs mpi oon the listed hosts

        :param names:
        :type names:
        :return:
        :rtype:
        """
        self.hosts = Parameter.expand(names)
        raise NotImplementedError

    def run(self, hosts=None, parameters=None, command=None):
        """
        runs mpirun on the listed hosts withthe given parameters and the given
        command. However, you can also use the regualr mpirun command.

        :param hosts:
        :type hosts:
        :param parameters:
        :type parameters:
        :param command:
        :type command:
        :return:
        :rtype:
        """
        self.hosts = Parameter.expand(hosts)

        raise NotImplementedError


    def create_hosts(self, hosts=None):
        """
        creates a hostfile for mpirun

        :param hosts:
        :type hosts:
        :return:
        :rtype:
        """
        self.hosts = Parameter.expand(hosts)

        raise NotImplementedError