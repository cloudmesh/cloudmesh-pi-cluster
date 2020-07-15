import os
import subprocess
import shutil
import socket
import fcntl
import struct

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.Host import Host
from cloudmesh.common.JobSet import JobSet
import platform
import sys
from cloudmesh.common.util import banner
from pprint import pprint
import textwrap
from cloudmesh.common.Tabulate import Printer

class Mongo:

    def execute(self, arguments):
        """
        pi mongo check [--master=MASTER] [--workers=WORKERS]
        pi mongo install [--master=MASTER] [--workers=WORKERS]
        pi mongo start --master=MASTER
        pi mongo stop --master=MASTER
        pi mongo test --master=MASTER
        pi mongo uninstall --master=MASTER [--workers=WORKERS]

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        master = []
        hosts = []
        if arguments.master:
            hosts.append(arguments.master)

        if arguments.workers:
            hosts = hosts + Parameter.expand(arguments.workers)

        if arguments.dryrun:
            self.dryrun = True

       # if hosts is None:
       #     Console.error("You need to specify at least one master or worker")
       #     return ""

        if arguments.install:
            self.install(master, hosts)

        elif arguments.start:
            print("Start Mongo")
            # self.run_script(name="spark.start", hosts=master)

        elif arguments.stop:
            print("Stop Mongo")
            # self.run_script(name="spark.stop", hosts=master)

        elif arguments.test:
            print("Test Mongo")
            # self.test(master)
            #self.run_script(name="spark.test", hosts=self.master)

        elif arguments.check:
            Console.msg("Checking Mongo ")
            if (shutil.which("mongo") or shutil.which("mongod")) is None:
                Console.error("Mongo installation not found.\n Install using the following command \n\n"
                              "pi mongo install [--master=MASTER] [--workers=WORKERS]")
            else:
                output = subprocess.check_output('mongo --version', shell=True)
                Console.msg(output.decode('utf-8'))

        elif arguments.uninstall:
            print("Remove Mongo")
            # self.uninstall(master, workers_only)

    def install(self, master, hosts):
        Console.msg("Installing...")
