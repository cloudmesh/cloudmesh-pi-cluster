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
from pprint import pprint

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
#from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer


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
        return msg.replace("\n", "").replace("  ", " ")

    @staticmethod
    def get_manager_ip_address(ifname):
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
        pi k3 install [--manager=MANAGER] [--workers=WORKERS] [--step=COMMAND]
        pi k3 join --manager=MANAGER --workers=WORKERS
        pi k3 uninstall [--manager=MANAGER] [--workers=WORKERS]
        pi k3 delete --workers=WORKERS
        pi k3 test [--manager=MANAGER] [--workers=WORKERS]
        pi k3 view
        pi k3 add_c_groups NAMES
        :param arguments:
        :return:
        """

        manager = None
        if arguments.manager:
            manager = arguments.manager

        hosts = None
        if arguments.workers:
            hosts = Parameter.expand(arguments.workers)

        step = None
        if arguments['--step']:
            step = arguments['--step']

        # if hosts is None:
        #    Console.error("You need to specify at least one worker")
        #    return ""

        # if manager is None:
        #    Console.error("You need to specify a manager")
        #    return ""

        if arguments.install:
            self.install(manager, hosts, step)

        if arguments.join:
            self.join(manager, hosts)

        if arguments.uninstall:
            self.uninstall(manager, hosts)

        if arguments.delete:
            self.delete(manager, hosts)

        if arguments.test:
            self.test(manager, hosts)

        if arguments.view:
            self.view()

        if arguments.add_c_groups:
            self.add_c_groups(arguments.NAMES)


    def enable_containers(self, filename="/boot/cmdline.txt", hosts=None):
        line = "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory"
        warning = "Your manager already has containers enabled"
        self.add_to_file(filename, line, warning)

        if hosts is not None:
            # Create tmp file on manager with enable_containers line
            source = "~/container_tmp.txt"
            command = f'echo "{line}" >> {source}'
            os.system(command)

            # Copy over temporary file with container line
            for host in hosts:
                command = "scp {0} pi@{1}:~/".format(source, host)
                os.system(command)

            # Check if workers already have line and if not,
            # append to /boot/cmdline.txt
            tmp_cmdline = "~/cmdline.txt"
            command = f"""
                if grep -q "{line}" '/boot/cmdline.txt'
                then
                  rm {source};
                else
                  cp /boot/cmdline.txt {tmp_cmdline};
                  cat {source} >> {tmp_cmdline};
                  sudo cp {tmp_cmdline} {filename}; rm {tmp_cmdline} {source};
                fi"""

            jobSet = JobSet("kubernetes_worker_enable_containers",
                            executor=JobSet.ssh)
            for host in hosts:
                jobSet.add({"name": host, "host": host, "command": command})
            jobSet.run()
            # jobSet.Print()

            # Delete tmp file on manager
            command = f"rm {source}"
            os.system(command)

    def install(self, manager=None, hosts=None, step=None):
        # Setup containers on manager
        if manager is None and hosts:
            Console.error("You must specify a manager to set up nodes")
            raise ValueError

        if step is not None:
            if step in 'enable_containers':
                self.enable_containers(hosts=hosts)

        # Install K3S on the manager
        if manager is not None:

            if type(manager) != list:
                manager = Parameter.expand(manager)

            #
            # TODO - bug I should be able to run this even if I am not on manager
            #
            banner(f"Setup Manager: {manager[0]}")

            command = Installer.oneline(f"""
            curl -sfL https://get.k3s.io | sh -
            """)
            jobSet = JobSet("kubernetes_manager_install", executor=JobSet.ssh)
            jobSet.add(
                {"name": self.hostname, "host": manager[0], "command": command})
            jobSet.run()
            result_stdout = jobSet.array()[0]['stdout'].decode('UTF-8')
            if "No change detected" in result_stdout:
                print()
                Console.info("Service already running")

        # Setup workers and join to cluster
        #
        # TODO - bug I should be able to run this even if I am not on manager
        #
        if hosts is not None:
            if manager is not None:
                banner(f"Get Join Token From {manager[0]}")
                command = "sudo cat /var/lib/rancher/k3s/server/node-token"
                jobSet = JobSet("kubernetes_token_retrieval",
                                executor=JobSet.ssh)
                jobSet.add(
                    {"name": manager[0], "host": manager[0], "command": command})
                jobSet.run()
                token = jobSet.array()[0]['stdout'].decode('UTF-8')

                # Install kubernetes to workers
                workers = ', '.join(hosts)
                banner(f"Setup Workers: {workers}")

                command = "curl -sfL http://get.k3s.io | sh -"
                # worker_install = Host.ssh(hosts=hosts,
                #                           command=command,
                #                           executor=os.system)

                jobSet = JobSet("kubernetes_worker_install",
                                executor=JobSet.ssh)
                for host in hosts:
                    jobSet.add({"name": host, "host": host, "command": command})
                jobSet.run(parallel=len(hosts))
                jobSet.Print()

                # Join workers to manager's cluster
                # TODO - Currently get ip address from eth0 instead of using
                #        hostname
                # because worker does not know manager's host name
                ip = self.get_manager_ip_address('eth0')

                command = f"""sudo k3s agent --server https://{ip}:{self.port} 
                --token {token}"""

                # TODO - This currently does not work, command runs fine but
                # "k3s agent" having trouble creating node. 
                jobSet = JobSet("kubernetes_worker_join", executor=JobSet.ssh)
                for host in hosts:
                    jobSet.add({"name": host, "host": host, "command": command})
                jobSet.run(parallel=len(hosts))
                jobSet.Print()
            else:
                Console.warning(
                    "You must have the manager parameter set to burn workers")

        # Print created cluster
        self.view()

    def join(self, manager=None, hosts=None):
        if hosts is not None and manager is not None:
            banner(f"Get Join Token From {manager}")
            command = "sudo cat /var/lib/rancher/k3s/server/node-token"
            jobSet = JobSet("kubernetes_token_retrieval", executor=JobSet.ssh)
            jobSet.add({"name": manager, "host": manager, "command": command})
            jobSet.run()
            token = jobSet.array()[0]['stdout'].decode('UTF-8')

            # TODO - Currently get ip address from eth0 instead of using
            #        hostname
            # because worker does not know manager's host name
            ip = self.get_manager_ip_address('eth0')

            command = f"""
            sudo k3s agent --server https://{ip}:{self.port}
            --token {token}"""

            jobSet = JobSet("kubernetes_worker_join", executor=JobSet.ssh)
            for host in hosts:
                jobSet.add({"name": host, "host": host, "command": command})
            jobSet.run(parallel=len(hosts))
            jobSet.Print()

            self.view()

    def uninstall(self, manager=None, hosts=None):
        # Uninstall manager
        if manager is not None:
            banner(f"Uninstalling Manager {manager}")

            command = "/usr/local/bin/k3s-uninstall.sh"
            jobSet = JobSet("kubernetes_manager_uninstall", executor=JobSet.ssh)
            jobSet.add({"name": manager, "host": manager, "command": command})
            jobSet.run()
            jobSet.Print()

        # Uninstall workers
        if hosts is not None:
            workers = ', '.join(hosts)
            banner(f"Uninstalling Workers: {workers}")
            # command = "/usr/local/bin/k3s-agent-uninstall.sh"
            command = "/usr/local/bin/k3s-uninstall.sh"
            jobSet = JobSet("kubernetes_worker_uninstall", executor=JobSet.ssh)

            for host in hosts:
                jobSet.add({"name": host, "host": host, "command": command})

            jobSet.run(parallel=len(hosts))
            jobSet.Print()

            self.delete(hosts=hosts)
            # print("Workers:", Printer.write(jobSet.array(),
            #        order=["name", "command", "status", "stdout",
            #               "returncode"]))

    def delete(self, manager=None, hosts=None):
        # Delete manager node
        # TODO - k3s does not allow you to delete it's parent node
        # if manager is not None:
        #    banner(f"Deleting Manager Node: {manager}")
        #
        #    command = Installer.oneline(f"""
        #                sudo kubectl delete {manager}
        #    """)
        #    jobSet = JobSet("kubernetes_manager_delete", executor=JobSet.ssh)
        #    jobSet.add({"name": self.hostname, "host": manager,
        #                "command": command})
        #    jobSet.run()

        # Uninstall workers
        if hosts is not None:
            workers = ', '.join(hosts)
            banner(f"Deleting Worker Node(s): {workers}")

            jobSet = JobSet("kubernetes_worker_delete", executor=JobSet.ssh)
            for host in hosts:
                command = Installer.oneline(f"""
                sudo kubectl drain {host} --ignore-daemonsets --delete-local-data; 
                sudo kubectl delete node {host}
                """)
                jobSet.add({"name": self.hostname, "host": self.hostname,
                            "command": command})
            jobSet.run(parallel=len(hosts))
            print("Workers:", Printer.write(jobSet.array(),
                                            order=["name", "command", "status",
                                                   "stdout", "returncode"]))

    def test(self, manager=None, hosts=None):
        print("Test not yet implemented")
        # TODO - Check for software that is installed or can be installed
        #        to run a test
        # on the cluster

    def view(self):
        os.system("sudo kubectl get node -o wide")
        # TODO - What other information about the chuster can I present

    def _print(self,results):
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def add_c_groups(self, names):
        names = Parameter.expand(names)
        Console.info(f'Enabling cgroups for {names}')
        cgroups = 'cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory'
        command = f"""if test -f /boot/firmware/cmdline.txt
                then
                  FILE=/boot/firmware/cmdline.txt
                elif test -f /boot/cmdline.txt
                then
                  FILE=/boot/cmdline.txt    
                fi              
                if grep -q "{cgroups}" $FILE
                then
                  true
                else
                  sudo sed -i "$ s/$/ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory/" $FILE
                fi"""

        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

        manager, workers = Host.get_hostnames(names)

        command = 'sudo reboot'
        if workers:
            Console.info(f'Executing `{command}` for {workers}')
            Host.ssh(hosts=workers, command=command)

        if manager:
            Console.info(f'Executing `{command}` for {manager}')
            Host.ssh(hosts=manager, command=command)

        # JOBSET VERSION WILL DELETE after confirm this is not preferred
        """        
        jobSet = JobSet("kubernetes_enable_containers",
                        executor=JobSet.ssh)
        for host in names:
            jobSet.add({"name": host, "host": host, "command": command})
        jobSet.run()
        #jobSet.Print()

        d = dict(jobSet.job)
        for host,v in d.items():
           if d[host]["returncode"] == 0 and d[host]["stdout"] == b"":
                print(f'Host: {host} SUCCESS')
           else:
                print(f'Host: {host} FAIL')
                pprint(d[host])

        Console.info(f"Rebooting {names}")

        manager, workers = Host.get_hostnames(names)

        command = 'sudo shutdown -h now'

        if workers:
            jobSet = JobSet("kubernetes_reboot",
                            executor=JobSet.ssh)
            for host in workers:
                jobSet.add({"name": host, "host": host, "command": command})
            jobSet.run()

        if manager:
            jobSet = JobSet("kubernetes_reboot",
                            executor=JobSet.ssh)
            jobSet.add({"name": manager, "host": manager, "command": command})
            jobSet.run()
        """


