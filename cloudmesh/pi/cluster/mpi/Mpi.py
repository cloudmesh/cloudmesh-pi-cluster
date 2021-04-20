from cloudmesh.common.parameter import Parameter
class Mpi:
"""
pi mpi install [NAMES]
pi mpirun [--hosts=HOSTS] --parameters=PARAMETERS] COMMAND
"""
    def __init__(self):
        self.hosts = None
        raise NotImplementedError

    def install(self, names):
        self.hosts = Parameter.expand(names)
        raise NotImplementedError

    def run(self, hosts=None, parameters=None, command=None):
        raise  NotImplementedError


