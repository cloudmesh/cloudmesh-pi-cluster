# cms pi k3 install --master=red --worker[01-03] --install=red02
#
# Meaning overall we like to have a clusetr with master and workers, but in this
# command we only deal with the install of node red002. However this node may
# need information from the master and workers to complete, so we put it in the
# commandline otions also. If the install is ommitted, the install is conducted
# on all nodes.
#
# We also want to add the feature of a step wise install
#
# cms pi k3 install --master=red --worker[01-03] --install=red02
#                   --step=enable_containers
#
# How do weget there?
#
# Let us look at teh seemingly simple description to add a line to a file.
#
# This can be comletely automated and we provide here a simple start (not yet
# Please remember that cloudmesh has a parallel execution framework for using
# ssh on remote machines
#
# cloudmesh.host.Host.ssh
#
# please learn about it as we in the second step can use this to run things in
# parallel on multiple hosts
#
# So lets get that example started:
#

import os
import subprocess

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.Host import Host

class Installer:

    @staticmethod
    def add_to_file(self, filename, line, warning=None):
        """
        adds a line to  a file if it is not already in it

        :return:
        """
        lines = readfile(filename)
        if line in lines:
            Console.warning(warning)
            return
        else:
            lines += f"\n{line}\n"
            writefile(filename, lines)

    def reboot(self):
        os.system("shutdown -r now")


class k3(Installer):
    def execute(self, arguments):
        """
        pi k3 install --master=MASTER --workers=WORKERS

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        hosts = []
        if arguments.master:
            master = arguments.master
        if arguments.workers:
            hosts = Parameter.expand(arguments.workers)

        step = None
        if arguments.step:
            step = arguments.step

        if hosts is None:
            Console.error("You need to specify at least one worker")
            return ""

        if master is None:
            Console.error("You need to specify a master")
            return ""

        if arguments.install:
            self.install(master, hosts, step)


    def enable_containers(self, filename="/boot/cmdline.txt"):
        line = "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory"
        warning = "You already have containers enabled"
        self.add_to_file(self, filename, line, warning)

    # cms pi k3 install --master=red --worker[01-03]
    #TODO - Add --install param
    def install(self, master=None, hosts=None, step=None):
        # Setup containers on master
        #TODO - Setup containers on workers too? 
        if step is 'enable_containers':
            self.enable_containers()

        # Install K3S on the master
        os.system("curl -sfL https://get.k3s.io | sh -")

        # Get join token from master
        task = subprocess.Popen(["sudo", "cat", "/var/lib/rancher/k3s/server/node-token"], stdout=subprocess.PIPE)
        for line in task.stdout:
            token = line.split()

        # Setup workers and join to cluster
        command = "curl -sfL http://get.k3s.io | K3S_URL=https://{0}:6443 K3S_TOKEN={1} sh -".format(master, token[0].decode('utf-8'))
        install = Host.ssh(hosts=hosts, command=command, executor=os.system)
        print(install)

        # Print created cluster
        os.system("sudo kubectl get node")
