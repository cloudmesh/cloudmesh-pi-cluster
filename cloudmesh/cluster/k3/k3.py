# cms pi k3 install --master=red --worker[01-03] --install=red02
#
# Meaning overall we like to have a clusetr with master and workers, but in this
# command we only deal with the install of node red002. However this node may
# need information from the master and workers to complete, so we put it in the
# commandline otions also. If the install is ommitted, the install is conducted
# on all nodes.

import os
import subprocess

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.Host import Host


class Installer:

    @staticmethod
    def add_to_file(filename, line, warning=None):
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


    def __init__(self):
        self.port = 6443

    def execute(self, arguments):
        """
        pi k3 install --master=MASTER --workers=WORKERS [--step=COMMAND]
        pi k3 uninstall [--master=MASTER] [--workers=WORKERS]
        pi k3 delete --workers=WORKERS
        pi k3 test --master=MASTER --workers=WORKERS
        pi k3 view
        :param arguments:
        :return:
        """

        master = None
        if arguments.master:
            master = arguments.master

        hosts = None
        if arguments.workers:
            hosts = Parameter.expand(arguments.workers)

        step = None
        if arguments['--step']:
            step = arguments['--step']

        # if hosts is None:
        #    Console.error("You need to specify at least one worker")
        #    return ""

        # if master is None:
        #    Console.error("You need to specify a master")
        #    return ""

        if arguments.install:
            self.install(master, hosts, step)

        if arguments.uninstall:
            self.uninstall(master, hosts)

        if arguments.delete:
            self.delete(hosts)

        if arguments.test:
            self.test(master, hosts)

        if arguments.view:
            self.view()

    def enable_containers(self, filename="/boot/cmdline.txt", hosts=None):
        line = "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory"
        warning = "Your master already has containers enabled"
        self.add_to_file(self, filename, line, warning)

        if hosts is not None:
            # Create tmp file on master with enable_containers line
            source = "~/container_tmp.txt"
            command = 'echo "{0}" >> {1}'.format(line, source)
            os.system(command)

            # Scp tmp file to each worker (TODO - Couldn't find Host.scp?)
            for host in hosts:
                command = "scp {0} pi@{1}:~/".format(source, host)
                os.system(command)

            # Check if workers already have line and if not, append to /boot/cmdline.txt
            tmp_cmdline = "~/cmdline.txt"
            command = """
                if grep -q '{line}' '/boot/cmdline.txt';
                then
                  rm {source}; 
                else cp /boot/cmdline.txt {tmp_cmdline}; 
                  cat {source} >> {tmp_cmdline}; 
                  sudo cp {tmp_cmdline} {filename}; rm {tmp_cmdline} {source};
                fi
                """.replace("\n","").replace("  ", " ")
            print (command)
            Host.ssh(hosts=hosts, command=command, executor=os.system)

            # Delete tmp file on master
            command = "rm {0}".format(source)
            os.system(command)

    # TODO - Add --install param (as in only install on the worker I specify)
    def install(self, master=None, hosts=None, step=None):
        # Setup containers on master
        if step is not None:
            # TODO - Add other steps eventually
            if step in 'enable_containers':
                self.enable_containers(hosts=hosts)

        # Install K3S on the master
        # TODO - Currently workers cant join because of CA Cert issue.
        # Can it be fixed here if I set server --tls-san or --bind-address params?
        os.system("curl -sfL https://get.k3s.io | sh -")
        #would Shell.live work? e.g. we can redirect stdin and stdout and check for errir?

        # Get join token from master
        task = subprocess.Popen(
            ["sudo", "cat", "/var/lib/rancher/k3s/server/node-token"],
            stdout=subprocess.PIPE)
        for line in task.stdout:
            token = line.split()

        # Setup workers and join to cluster
        #
        # make port a
        command = "curl -sfL http://get.k3s.io | K3S_URL=https://{0}:{self.port} K3S_TOKEN={1} sh -".format(
            master, token[0].decode('utf-8'))
        install = Host.ssh(hosts=hosts, command=command, executor=os.system)
        print(install)

        # Print created cluster
        os.system("sudo kubectl get nodes")

    def uninstall(self, master=None, hosts=None):
        # Uninstall master
        if master is not None:
            os.system("/usr/local/bin/k3s-uninstall.sh")

        # Uninstall workers
        if hosts is not None:
            command = "/usr/local/bin/k3s-agent-uninstall.sh"
            uninstall = Host.ssh(hosts=hosts, command=command,
                                 executor=os.system)
            print(uninstall)

    def delete(self, hosts=None):
        print("Delete not yet implemented")
        # TODO - delete node from master's cluster
        # I believe the command is "kubectl delete [NODE NAME]

    def test(self, master=None, hosts=None):
        print("Test not yet implemented")
        # TODO - Check for software that is installed or can be installed to run a test
        # on the cluster

    def view(self):
        os.system("sudo kubectl get node -o wide")
        # TODO - What other information about the chuster can I present
