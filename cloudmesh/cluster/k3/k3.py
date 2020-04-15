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
import platform
import sys
from cloudmesh.common.util import banner
from pprint import pprint
import textwrap

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

    @staticmethod
    def reboot():
        os.system("shutdown -r now")

    @staticmethod
    def oneline(msg):
        return msg.replace("\n", "").replace ("  ", " ")


class K3(Installer):


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
        self.add_to_file(filename, line, warning)

        if hosts is not None:
            # Create tmp file on master with enable_containers line
            source = "~/container_tmp.txt"
            command = f'echo "{line}" >> {source}'
            os.system(command)

            # Scp tmp file to each worker (TODO - Couldn't find Host.scp?)
            for host in hosts:
                command = "scp {0} pi@{1}:~/".format(source, host)
                os.system(command)

            # Check if workers already have line and if not, append to /boot/cmdline.txt
            tmp_cmdline = "~/cmdline.txt"
            command = Installer.oneline(f"""
                if grep -q '{line}' '/boot/cmdline.txt';
                then
                  rm {source};
                else cp /boot/cmdline.txt {tmp_cmdline};
                  cat {source} >> {tmp_cmdline};
                  sudo cp {tmp_cmdline} {filename}; rm {tmp_cmdline} {source};
                fi""")
            print(command)
            Host.ssh(hosts=hosts, command=command, executor=os.system)

            # Delete tmp file on master
            command = f"rm {source}"
            os.system(command)

    def install(self, master=None, hosts=None, step=None):
        # Setup containers on master

        if master is None and hosts:
            Console.error("You must specify a master to set up nodes")
            raise ValueError

        if step is not None:
            if step in 'enable_containers':
                self.enable_containers(hosts=hosts)

        # Install K3S on the master
        if master is not None:

            if type(master) != list:
                master = Parameter.expand(master)

            #
            # bug I shoudl be able to run this even if I am not on master
            #
            banner(f"Setup Master {master}")

            command = Installer.oneline(f""" 
                      echo "Hostname:" `hostname`; echo;
                      curl -sfL https://get.k3s.io | sh -
                      """)
            result = Host.ssh(hosts=master, command=command, executor=os.system)[0]
            if "No change detected" in result.stdout:
                print()
                Console.info("Service already running")


            banner(f"Get Token {master}")

            command = "sudo cat /var/lib/rancher/k3s/server/node-token"
            token = Host.ssh(hosts=hosts, command=command, executor=os.system)[0]
            token = token.stdout

            print("Token:", token)




        # Setup workers and join to cluster

        #
        # bug I shoudl be able to run this even if I am not on master
        #
        workers = ', '.join(hosts)
        banner(f"Install workers: {workers}")
        if hosts is not None:
            if master is not None:


                # TODO - Currently workers cant join because of CA Cert issue.
                # Can it be fixed here if I set server --tls-san or --bind-address params?
                # TODO - I add .local to {master} param, should I remove later?
                command = Installer.oneline(f"""
                            echo "Hostname:" `hostname`; echo;
                            curl -sfL http://get.k3s.io | 
                            K3S_URL=https://{master}.local:{self.port} 
                            K3S_TOKEN={token} sh -
                """)
                install = Host.ssh(hosts=hosts, command=command, executor=os.system)
                print(install)
            else:
                Console.warning("You must have the master parameter set to burn workers")

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
