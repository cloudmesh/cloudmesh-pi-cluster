import sys
import platform
import os
import subprocess
import textwrap
# Functions in utils should be moved to cloudmesh.common
from utils import *

from cloudmesh.common.Printer import Printer
# from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import writefile
from cloudmesh.common.util import yn_choice

#
# These methods are not parallel but just work in one processor
#

class Bridge:
    """
    A simple Bridge to connect workers to the internet through a port on the master
    """

    dryrun = False
    ext_interface = "eth1"
    priv_interface = "eth0"
    master = None
    workers = None

    @classmethod
    def create(cls, master=None, workers=None, priv_interface='eth0', ext_interface='eth1', dryrun=False):
        """
        if worker(s) is missing the master is set up only
        if master is missing only the worker is set up

        :param master: expected to be a single string
        :param workers:
        :param ext_interface: The external interface through which the master connects to the internet
        :param priv_interface: The private interface through which the master and workers communicate
        :param dryrun:
        :return:
        """
        cls.master = master
        cls.workers = workers
        cls.dryrun = dryrun
        cls.ext_interface = ext_interface
        cls.priv_interface = priv_interface

        if master is None or ext_interface == 'wlan0':
            raise NotImplementedError

        StopWatch.start('Enable iPv4 forwarding')
        cls._set_ipv4()
        StopWatch.stop('Enable iPv4 forwarding')
        StopWatch.status('Enable iPv4 forwarding', True)

        StopWatch.start('iptables configuration')
        cls._set_iptables()
        StopWatch.stop('iptables configuration')
        StopWatch.status('iptables configuration', True)

        Console.info("Finished configuration of master")

        if workers is None:
            return

        Console.info("Starting configuration for workers")
        Console.error("Not implemented")
        sys.exit(1)
            
    # Set a worker to use the master
    @classmethod
    def set(cls, master=None, worker=None, name=None):
        raise NotImplementedError

    @classmethod
    def list(cls, host=None):
        raise NotImplementedError

    @classmethod
    def check(cls, host=None):
        raise NotImplementedError

    @classmethod
    def restart(cls, host=None):
        raise NotImplementedError

    # Begin private methods for Bridge
    @classmethod
    def _system(cls, command):
        """
        :param command:
        :return: stdout of command
        """
        res = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        if res[0] != 0:
            Console.warning(f'Warning: "{command}" did not execute properly -> {res[1]} :: exit code {res[0]}')

        return res[1]
    
    @classmethod
    def _set_ipv4(cls):
        """
        Turns on iPv4 Forwarding on the system
        and saves rules upon eventual reboot

        :param dryrun:
        :return:
        """
        if cls.dryrun:
            Console.info("DRYRUN: Turning on iPv4")
        else:
            new_line='net.ipv4.ip_forward=1'

            # First turn on ipv4 forwarding
            cls._system(f'sudo sysctl -w {new_line}')

            # Save for next boot
            old_conf = sudo_readfile('/etc/sysctl.conf')

            if new_line not in old_conf:
                # The default sysctl has the new_line commented out. Try to uncomment it
                try:
                    old_conf[old_conf.index('#' + new_line)] = new_line
                except ValueError:
                    Console.warning("Could not find iPv4 setting. Perhaps /etc/sysctl.conf has been changed from default. Process continues by adding iPv4 setting")
                    old_conf.append('net.ipv4.ip_forward=1')
                except:
                    Console.error("Could not set iPv4 forwarding. Unknown error occurred")
                finally:
                    sudo_writefile('/etc/sysctl.conf', '\n'.join(old_conf))
            else:
                Console.info("iPv4 forwarding already set. Skipping iPv4 setup")


    @classmethod
    def _set_iptables(cls):
        """
        Sets up routing in iptables and saves rules for eventual reboot

        :return:
        """
        cmd1 = f"sudo iptables -A FORWARD -i {cls.priv_interface} -o {cls.ext_interface} -j ACCEPT"
        cmd2 = f"sudo iptables -A FORWARD -i {cls.ext_interface} -o {cls.priv_interface} -m state --state ESTABLISHED,RELATED -j ACCEPT"
        cmd3 = f"sudo iptables -t nat -A POSTROUTING -o {cls.ext_interface} -j MASQUERADE"

        if cls.dryrun:
            Console.info("DRYRUN: Setting iptables")
            print(f"DRYRUN: {cmd1}")
            print(f"DRYRUN: {cmd2}")
            print(f"DRYRUN: {cmd3}")

        else:
            cls._system(cmd1)
            cls._system(cmd2)
            cls._system(cmd3)

            # Save rules
            cls._system('sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"')

            # Restore rules if reboot
            old_conf = sudo_readfile('/etc/rc.local', trim=True)
            
            # Exit 0 should be in the last entry of old_conf 
            # Add ip table restoration lines just above
            restore_command = "iptables-restore < /etc/iptables.ipv4.nat"

            if old_conf[-1] != 'exit 0':
                Console.error('rc.local does not have exit 0 in last line. Contingency not handled in this version. Cannot enable iPv4 forwarding at this time')
                raise NotImplementedError

            if restore_command not in old_conf:
                old_conf.append(restore_command)
                old_conf[-1], old_conf[-2] = old_conf[-2], old_conf[-1] # Places 'exit 0' below our restore_command
                sudo_writefile('/etc/rc.local', '\n'.join(old_conf) + '\n')

            else:
                Console.warning(f"iptables restoration already in rc.local")

            




# Tests
Bridge.create(master='red', priv_interface='eth0', ext_interface='eth1', dryrun=False)
StopWatch.benchmark(sysinfo=False, csv=False, tag='MasterConfig')
