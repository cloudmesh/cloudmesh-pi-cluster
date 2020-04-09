import sys
import subprocess
import textwrap
# Functions in utils should be moved to cloudmesh.common
from cloudmesh.bridge.utils import *

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import writefile, readfile

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
    dns=['8.8.8.8', '8.8.4.4']

    @classmethod
    def create(cls, master=None, workers=None, priv_interface='eth0', ext_interface='eth1', dryrun=False):
        """
        if worker(s) is missing the master is set up only

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

        if master is None:
            Console.error("No master provided")
            sys.exit(1)

        # Master configuration
        StopWatch.start('Master Configuration')

        # iPv4 forwarding
        StopWatch.start('Enable iPv4 forwarding')
        cls._set_ipv4()
        StopWatch.stop('Enable iPv4 forwarding')
        StopWatch.status('Enable iPv4 forwarding', True)

        # iptables configuration
        StopWatch.start('iptables configuration')
        cls._set_iptables()
        StopWatch.stop('iptables configuration')
        StopWatch.status('iptables configuration', True)

        StopWatch.stop('Master Configuration')
        StopWatch.status('Master Configuration', True)

        Console.info("Finished configuration of master")

        if workers is None:
            Console.warning("No workers to configure")
            Console.ok("Process completed for master only")
            return

        # Worker configuration
        StopWatch.start('Configuration of workers')
        Console.info("Starting configuration for workers")
        for worker in workers:
            cls._configure_worker_interfaces(worker=worker, user='pi')
        StopWatch.stop('Configuration of workers')
        StopWatch.status('Configuration of workers', True)

        Console.ok("Process completed")
        banner(textwrap.dedent("""
        You have now configured a bridge between your worker(s) and master. To see the effects, you must restart your network interfaces.
        To do so, simply call

        cms bridge restart

        """), color='CYAN')

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
    def restart(cls, master=None, workers=None, user='pi'):
        if master is not None:
            banner("Restart networking service on master...", color='CYAN')
            status = cls._system('sudo service networking restart', exitcode=True)
            if status != 0:
                Console.error('Did not restart {master} networking service correctly')
                sys.exit(1)

            Console.ok("Restarted networking service on master")

        if workers is not None:
            banner("Restart networking service on workers...", color='CYAN')
            for worker in workers:
                status = cls._system(f'ssh {user}@{worker} sudo service networking restart', exitcode=True)
                if status != 0:
                    Console.error(f'Did not restart {worker} networking service correctly')
                    sys.exit(1)

            Console.ok("Restarted networking service on workers")

    # Begin private methods for Bridge
    @classmethod
    def _system(cls, command, exitcode=False):
        """
        :param command:
        :param exitcode: True if we only want exitcode
        :return: stdout of command
        """
        exit, stdout = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        if exit != 0:
            Console.warning(f'Warning: "{command}" did not execute properly -> {stdout} :: exit code {exit}')

        if exitcode:
            return exit
        else:
            return stdout
    
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
    def _set_iptables(cls, flush=True):
        """
        Sets up routing in iptables and saves rules for eventual reboot

        :flush: Remove all rules for related iptables
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
            if flush:
                cls._system('sudo iptables --flush')
                cls._system('sudo iptables -t nat --flush')

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

    @classmethod
    def _configure_worker_interfaces(cls, worker, user='pi'):
        """
        Configures the network interface of the worker to use the master as an internet gateway

        :param worker: A single string hostname for the worker (ie. --hostname option from cm-pi-burn)
        :param user: The user we will use to ssh/scp into the worker
        :return:
        """

        if cls.dryrun:
            Console.info("Configuring worker info.")
            Console.info(f"scp /etc/network/interfaces from {cls.master} to {user}@{worker}")
            Console.info("Configure default gateway and DNS for {cls.priv_interface} on {user}@{worker}")

        else:
            # Get gateway and netmask for worker
            conf = cls._system('ifconfig')
            conf = conf.split('\n')

            # Search for priv_interface
            info = None
            for i in range(len(conf)):
                if cls.priv_interface in conf[i]:
                    info = conf[i + 1].split()
                    
            if info == None:
                Console.error(f"Interface {cls.priv_interface} not found")
                sys.exit(1)
            
            elif info[0] != 'inet':
                Console.error(f"Interface {cls.priv_interface} found, but there appears to be no iPv4 connection")
                sys.exit(1)

            else:
                # info ex: ['inet', '192.168.1.34', 'netmask', '255.255.255.0', 'broadcast', '192.168.1.255']
                gateway = info[1]
                netmask = info[3]

                # Use scp to get /etc/network/interfaces from worker
                cls._system('mkdir -p ~/.cloudmesh/tmp')
                tmp = f'~/.cloudmesh/tmp/{worker}-interfaces.tmp'

                StopWatch.start(f'Talking to {user}@{worker}')
                exit_code = cls._system(f'scp {user}@{worker}:/etc/network/interfaces {tmp}', exitcode=True)
                StopWatch.stop(f'Talking to {user}@{worker}')
                StopWatch.status(f'Talking to {user}@{worker}', exit_code == 0)

                # Write new interfaces file
                try:
                    interfaces = readfile(tmp).rstrip().split('\n')
                except:
                    Console.error(f"Could not open {tmp}")
                    sys.exit(1)

                try:
                    ind = interfaces.index(f'auto {cls.priv_interface}')
                except:
                    Console.error(f"Could not find {cls.priv_interface} configuration in interfaces file")

                interface_config = [line.lstrip() for line in interfaces[ind: ind + 3]]
                interface_config.append(f'gateway {gateway}')
                interface_config.append(f'netmask {netmask}')
                dnss = " ".join(cls.dns) + "\n"
                interface_config.append(f'dns-nameservers {dnss}')

                new_config = interfaces[:ind] + interface_config
                writefile(tmp, '\n'.join(new_config))

                # New config file now written on local machine. Move to worker in tmp directory
                remote_cmd1 = 'mkdir -p ~/.cloudmesh/tmp'
                remote_path = '~/.cloudmesh/tmp/interface.tmp'
                cls._system(f'scp {tmp} {user}@{worker}:{remote_path}')
                remote_cmd2 = 'sudo cp ~/.cloudmesh/tmp/interface.tmp /etc/network/interfaces'
                cls._system(f'ssh {user}@{worker} {remote_cmd2}')


# Tests
# Bridge.create(master='red', workers=['red001'], priv_interface='eth0', ext_interface='wlan0', dryrun=False)
# Bridge.restart(master='red', workers=['red001'])
# StopWatch.benchmark(sysinfo=False, csv=False, tag='Testing')
