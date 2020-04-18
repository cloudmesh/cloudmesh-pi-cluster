# cms pi k3 install --master=red --worker[01-03] --install=red02
#
# Meaning overall we like to have a clusetr with master and workers, but in this
# command we only deal with the install of node red002. However this node may
# need information from the master and workers to complete, so we put it in the
# commandline otions also. If the install is ommitted, the install is conducted
# on all nodes.

import os
import subprocess
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

    @staticmethod
    def get_master_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])

class K3(Installer):


    def __init__(self):
        self.port = 6443
        self.hostname = os.uname()[1]

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
            # TODO - Host.ssh(hosts=hosts, command=command, executor=os.system)
            jobSet = JobSet("kubernetes_worker_enable_containers", executor=JobSet.ssh)
            for host in hosts:
                print(host)
                jobSet.add({"name": host, "host": host, "command": command})
            jobSet.run(parallel=len(hosts))
            print(Printer.write(jobSet.array(),
                    order=["name", "command", "status", "stdout",
                           "returncode"]))

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
            # TODO - bug I should be able to run this even if I am not on master
            #
            banner(f"Setup Master: {master[0]}")

            command = Installer.oneline(f""" 
                      echo "Hostname:" `hostname`; echo;
                      curl -sfL https://get.k3s.io | sh -
                      """)
            jobSet = JobSet("kubernetes_master_install", executor=JobSet.ssh)
            jobSet.add({"name": self.hostname, "host": master[0], "command": command})
            jobSet.run()
            result_stdout = jobSet.array()[0]['stdout'].decode('UTF-8')
            if "No change detected" in result_stdout:
                print()
                Console.info("Service already running")


            banner(f"Get Token {master[0]}")

            command = "sudo cat /var/lib/rancher/k3s/server/node-token"
            jobSet = JobSet("kubernetes_token_retrieval", executor=JobSet.ssh)
            jobSet.add({"name": master[0], "host": master[0], "command": command})
            jobSet.run()
            token = jobSet.array()[0]['stdout'].decode('UTF-8')


        # Setup workers and join to cluster
        #
        # TODO - bug I should be able to run this even if I am not on master
        #
        workers = ', '.join(hosts)
        banner(f"Setup Workers: {workers}")
        if hosts is not None:
            if master is not None:
                # TODO - Currently get ip address from eth0 instead of using hostname
                # because worker does not know master's host name
                ip = self.get_master_ip_address('eth0')
                command = Installer.oneline("""
                            curl -sfL http://get.k3s.io
                            K3S_URL=https://{ip}:{self.port}
                            K3S_TOKEN={token} sh -
                """)
                jobSet = JobSet("kubernetes_worker_install", executor=JobSet.ssh)
                #TODO - Only works with one worker, does not work with multiple (runs on last one)
                for host in hosts:
                    jobSet.add({"name": host, "host": host, "command": command})
                #jobSet.add({"name": hostname, "host": hostname, "command": command})
                jobSet.run(parallel=len(hosts))
                jobSet.Print()
            else:
                Console.warning("You must have the master parameter set to burn workers")

        # Print created cluster
        os.system("sudo kubectl get nodes")


    def uninstall(self, master=None, hosts=None):
        # Uninstall master
        if master is not None:
            banner(f"Uninstalling Master {master}")

            command = Installer.oneline(f"""
                        /usr/local/bin/k3s-uninstall.sh
            """)
            jobSet = JobSet("kubernetes_master_uninstall", executor=JobSet.ssh)
            jobSet.add({"name": master, "host": master, "command": command})
            jobSet.run()

        # Uninstall workers
        if hosts is not None:
            workers = ', '.join(hosts)
            banner(f"Uninstalling Workers: {workers}")
            command = "/usr/local/bin/k3s-agent-uninstall.sh"
            jobSet = JobSet("kubernetes_worker_uninstall", executor=JobSet.ssh)

            for host in hosts:
                jobSet.add({"name": host, "host": host, "command": command})
            #jobSet.add({"name": hostname, "host": hostname, "command": command})

            jobSet.run(parallel=len(hosts))
            print("Workers:", Printer.write(jobSet.array(),
                    order=["name", "command", "status", "stdout", "returncode"]))


    def delete(self, master=None, hosts=None):
        # Delete master node
        # TODO - k3s does not allow you to delete it's parent node
        #if master is not None:
        #    banner(f"Deleting Master Node: {master}")
        #
        #    command = Installer.oneline(f"""
        #                sudo kubectl delete {master}
        #    """)
        #    jobSet = JobSet("kubernetes_master_delete", executor=JobSet.ssh)
        #    jobSet.add({"name": self.hostname, "host": master, "command": command})
        #    jobSet.run()

        # Uninstall workers
        if hosts is not None:
            workers = ', '.join(hosts)
            banner(f"Deleting Worker Node(s): {workers}")

            jobSet = JobSet("kubernetes_worker_delete", executor=JobSet.ssh)
            for host in hosts:
                command = Installer.oneline(f"""
                        sudo kubectl delete {host}
                """)
                jobSet.add({"name": master, "host": master, "command": command})
            #jobSet.add({"name": hostname, "host": hostname, "command": command})
            jobSet.run(parallel=len(hosts))
            print("Workers:", Printer.write(jobSet.array(),
                    order=["name", "command", "status", "stdout", "returncode"]))


    def test(self, master=None, hosts=None):
        print("Test not yet implemented")
        # TODO - Check for software that is installed or can be installed to run a test
        # on the cluster


    def view(self):
        os.system("sudo kubectl get node -o wide")
        # TODO - What other information about the chuster can I present
