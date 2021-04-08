import os
import subprocess
import fcntl
import struct
import platform
import sys
import textwrap
from pprint import pprint

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.Host import Host
from cloudmesh.common.JobSet import JobSet
from cloudmesh.common.util import banner
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer


class Installer:

    @staticmethod
    def _get_server_token(server):
        Console.info("Fetching the server token")

        command = "sudo cat /var/lib/rancher/k3s/server/node-token"
        results = Host.ssh(
            hosts=server,
            command=command
        )
        token = results[0]['stdout'].strip()

        if token == "" or "::server:" not in token:
            Console.error("Could not determine SERVER token")
            token = None
        #Console.info(f'token is {token}')
        return(token)

class K3(Installer):

    def __init__(self):
        pass

    def execute(self, arguments):
        """
        pi k3 add_c_groups NAMES
        pi k3 install server NAMES
        pi k3 install agent NAMES SERVER
        pi k3 install cluster NAMES
        pi k3 uninstall server NAMES
        pi k3 uninstall agent NAMES
        pi k3 uninstall cluster NAMES
        :param arguments:
        :return:
        """

        if arguments.install and arguments.server:
            self.install_server(arguments.NAMES)

        elif arguments.install and arguments.agent:
            self.install_agent(arguments.NAMES, arguments.SERVER)

        elif arguments.install and arguments.cluster:
            self.install_cluster(arguments.NAMES)

        elif arguments.uninstall and arguments.server:
            self.uninstall_server(arguments.NAMES)

        elif arguments.uninstall and arguments.agent:
            self.uninstall_agent(arguments.NAMES)

        elif arguments.uninstall and arguments.cluster:
            self.uninstall_cluster(arguments.NAMES)

        elif arguments.add_c_groups:
            self.add_c_groups(arguments.NAMES)

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

    def install_server(self,names):
        names = Parameter.expand(names)
        Console.info(f'Installing K3s as stand-alone server on {names}')
        command = f"curl -sfL https://get.k3s.io | sh -"

        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def install_agent(self,names,server):
        Console.info(f'Installing K3s on {names} as agent of {server}')

        names = Parameter.expand(names)
        #ip = self._get_server_ip(server)
        #if ip is None:
        #    return ""
        token = self._get_server_token(server)
        if token is None:
            return ""

        command = f"curl -sfL https://get.k3s.io | K3S_URL=https://{server}:6443 " \
                  f"K3S_TOKEN={token} sh -"

        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def install_cluster(self,names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)

        if manager is None:
            Console.error("A manager is required, if trying to install a "
                          "stand-alone cluster on a worker, use `cms pi k3 "
                          "install server``")
            return

        self.install_server(manager)
        self.install_agent(manager,manager)
        if workers:
            self.install_agent(workers,manager)

    def uninstall_server(self, names):
        Console.info(f'Uninstalling server install of K3s on {names}')

        names = Parameter.expand(names)
        command = "/usr/local/bin/k3s-uninstall.sh"

        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def uninstall_agent(self,names):
        Console.info(f'Uninstalling agent install of K3s on {names}')

        names = Parameter.expand(names)

        command = "/usr/local/bin/k3s-agent-uninstall.sh"
        results = Host.ssh(
            hosts=names,
            command=command
        )
        print(Printer.write(results,
                            order=['host', 'success', 'stdout'],
                            output='table'))

    def uninstall_cluster(self, names):
        names = Parameter.expand(names)
        manager, workers = Host.get_hostnames(names)

        self.uninstall_agent(names)
        self.uninstall_server(manager)








