import textwrap
import os

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.pi.cluster.k3.K3SDashboard import K3SDashboard
from cloudmesh.common.StopWatch import StopWatch



class Tensorflow:

    def __init__(self):
        pass

    def execute(self, arguments):

        arguments.NAMES = Parameter.expand_names(arguments.NAMES)

        if arguments.install and arguments.step1:
            StopWatch.start("install tensorflow step1")
            self.deploy_step1(arguments.NAMES)
            StopWatch.stop("install tensorflow step1")
            StopWatch.status("install tensorflow step1", True)
            StopWatch.print("install tensorflow step1")

        elif arguments.install and arguments.step2:
            StopWatch.start("install tensorflow step2")
            self.deploy_step2(arguments.NAMES)
            StopWatch.stop("install tensorflow step2")
            StopWatch.status("install tensorflow step2", True)
            StopWatch.print("install tensorflow step2")

        elif arguments.install and arguments.test:
            StopWatch.start("tensorflow test")
            self.deploy_test(arguments.NAMES)
            StopWatch.stop("tensorflow test")
            StopWatch.status("tensorflow test", True)
            StopWatch.print("tensorflow test")


    @staticmethod
    def _run_and_print(command, names):
        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def deploy_step1(self, names):
        command = "ls" # curl .....
        self._run_and_print(command, names)


    def deploy_step2(self, names):
        command = "ls"  # curl .....
        self._run_and_print(command, names)

    def test(self, names):
        command = "ls"  # curl .....
        self._run_and_print(command, names)
