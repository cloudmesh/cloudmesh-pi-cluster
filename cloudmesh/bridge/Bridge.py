import re
import sys
import textwrap
import time
from pathlib import Path

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
    A simple Bridge to connect workers to the internet through a port on the
    manager
    """

    dryrun = False
    ext_interface = "eth1"
    priv_interface = "eth0"
    lease = '12h'
    master = None
    masterIP = None
    ip_range = None
    workers = None
    dns = ['8.8.8.8', '8.8.4.4']
    lease_bookmark = '# LEASE HISTORY #'

    @classmethod
    def create(cls, masterIP='10.1.1.1', ip_range=['10.1.1.2', '10.1.1.122'],
               master=None, workers=None,
               priv_interface='eth0', ext_interface='eth1', purge=False,
               dryrun=False):
        """
        if worker(s) is missing the master is set up only

        :param master: expected to be a single string
        :param workers:
        :param ext_interface: The external interface through which the manager
                              connects to the internet
        :param priv_interface: The private interface through which the manager
                               and workers communicate
        :param dryrun:
        :return:
        """
        cls.masterIP = masterIP
        cls.ip_range = ip_range
        cls.master = master
        cls.workers = workers
        cls.dryrun = dryrun
        cls.ext_interface = ext_interface
        cls.priv_interface = priv_interface

        # Master configuration
        StopWatch.start('Manager Configuration')

        # Configure dhcpcd.conf of master. No restart
        StopWatch.start('dhcpcd.conf configuration')
        cls._dhcpcd_conf()
        StopWatch.stop('dhcpcd.conf configuration')
        StopWatch.status('dhcpcd.conf configuration', True)

        # if purge:
        #     # Uninstall dnsmasq and all files
        #     StopWatch.start('dnsmasq purge')
        #     cls._purge_dnsmasq()
        #     StopWatch.start('dnsmasq purge')
        #     StopWatch.status('dnsmasq purge', True)

        # Install dnsmasq if it is not already installed
        # if not cls._dnsmasq_exists():
        #     StopWatch.start('dnsmasq installation')
        #     cls._install_dnsmasq()
        #     StopWatch.stop('dnsmasq installation')
        #     StopWatch.status('dnsmasq installation', True)
        # else:
        #     Console.info("dnsmasq already installed. Skipping installation")

        # # Configure dnsmasq
        # StopWatch.start('dnsmasq config')
        # cls._config_dnsmasq()
        # StopWatch.stop('dnsmasq config')
        # StopWatch.status('dnsmasq config', True)

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

        StopWatch.stop('Manager Configuration')
        StopWatch.status('Manager Configuration', True)

        Console.info("Finished configuration of manager")

        cls._completion_message()

        Console.ok("Process completed")

    # Set a worker to use the master
    @classmethod
    def set(cls, workers=None, addresses=None):
        """
        Assigns static IP addresses to the workers

        :param workers: List of worker hostnames
        :param addresses: List of IP addresses
        """
        if cls.dryrun:
            Console.info(f"DRYRUN: Setting {workers} to {addresses}")
        else:
            if not Path('/etc/dnsmasq.conf').is_file():
                Console.error(
                    'This Pi is not configured as a bridge yet. '
                    'See "cms bridge create" ')
                sys.exit(1)

            elif len(workers) != len(addresses):
                Console.error(
                    'The number of hostnames and addresses given do not match')
                sys.exit(1)

            else:
                conf_line = cls._system(
                    'cat /etc/dnsmasq.conf | grep dhcp-range')
                interm = conf_line.split(',')
                upper = interm[1]  # 10.1.1.20
                lower = interm[0].split('=')[1]  # 10.1.1.2
                cls.ip_range = lower, upper

                to_add = []
                for i in range(len(workers)):
                    host = workers[i]
                    ip = addresses[i]
                    Console.info(f"Setting {host} to {ip}")

                    if not cls._in_range(ip):
                        Console.warning(
                            f"Suitable ip range is {cls.ip_range[0]} - {cls.ip_range[1]}")
                        Console.error(
                            f'Address {ip} for {host} is out of range. '
                            f'See "cms bridge create --range=RANGE" to reconfigure the IP range')
                        sys.exit(1)

                    # Check if static IP assignment already exists
                    conf = sudo_readfile('/etc/dnsmasq.conf')

                    start = f'dhcp-host={host}'
                    line = f'{start},{ip}'  # dhcp-host=red001,10.1.1.1
                    ipPattern = re.compile(f'dhcp-host=.*{ip}')
                    hostPattern = re.compile(f'{start}.*')

                    ipResults = list(filter(ipPattern.search,
                                            conf))  # see if ip is already assigned
                    hostResults = list(filter(hostPattern.search,
                                              conf))  # see if host is already assigned

                    # If ip already assigned
                    if ipResults:
                        Console.error(
                            f'{ip} is already assigned. Please try a different IP')
                        sys.exit(1)

                    # If new host
                    if not hostResults:
                        to_add.append(line)

                    else:
                        Console.warning(
                            f"Previous IP assignment for {host} found. Overwriting.")
                        if len(hostResults) > 1:
                            Console.warning(
                                f"Found too many assignments for {host}. Overwriting first one")
                        key = conf.index(hostResults[0])
                        conf[key] = line

                conf += to_add

                sudo_writefile('/etc/dnsmasq.conf', '\n'.join(conf) + '\n')
                Console.ok("Added IP's to dnsmasq")

    @classmethod
    def status(cls):
        """
        A simple status check of the bridge setup. It looks at both dhcpcd and dnsmasq status messages.
        """
        dhcpcdRunning = 'running' in cls._system(
            'sudo service dhcpcd status | grep Active', warnuser=False)
        dnsmasqRunning = 'running' in cls._system(
            'sudo service dnsmasq status | grep Active', warnuser=False)
        banner(textwrap.dedent(f"""
        Status of Bridge:

        DHCPCD     -  Service running: {dhcpcdRunning}
        DNSMASQ  -  Service running: {dnsmasqRunning}

        BRIDGE        - Service running: {dhcpcdRunning and dnsmasqRunning}
        
        """), color='CYAN')

    @classmethod
    def list(cls, host=None):
        raise NotImplementedError

    @classmethod
    def check(cls, hosts=None):
        raise NotImplementedError

    @classmethod
    def test(cls, hosts=None):
        """
        Command to test the connectivity to specified hostnames. First checks to see if the device has even registered
        with the bridge in ~/.cloudmesh/bridge/info which is a directory created when the bridge is first created.

        :param host: List of hostnames to check for connectivity.
        :return:
        """

        try:
            info = sudo_readfile('~/.cloudmesh/bridge/info')
            index = info.index(cls.lease_bookmark)
            leases = info[index + 1:]
        except Exception as e:
            Console.error(
                'Could not find information on bridge. Has the bridge been created yet?')
            sys.exit(1)

        known_hosts = []
        for lease in leases:
            lease_info = lease.split()
            host = lease_info[4]
            known_hosts.append(host)

        count = 0
        hosts_to_check = len(hosts)
        Console.info("Beginning ping checks...")
        for host in hosts:
            if host not in known_hosts:
                Console.warning(
                    f'{host} is not among the known devices of the bridge. '
                    f'No connection from {host} has been received before. Skipping test')
                hosts_to_check -= 1
            else:
                Console.info(f'Pinging Host {host}. Please wait ...')
                status, stdout = cls._system(f'ping -c 1 {host}',
                                             warnuser=False, both=True)
                # I believe this is a sufficient check
                if status != 0:
                    message = textwrap.dedent(f"""
                    Could not ping {host} successfuly.
                    
                    Rebooting {host} may fix the problem.

                    Manually ping {host} for more details.
                    """)
                    Console.warning(message)
                else:
                    count += 1
                    Console.ok(f"Successfuly pinged {host}")

        Console.ok(
            f'Completed checks. {count} out of {hosts_to_check} checks succeeded.')

    @classmethod
    def restart(cls, priv_iface='eth0', workers=None, user='pi', nohup=False):
        """
        :param workers: List of workers to restart if needed
        :return:
        """

        banner("Restarting bridge on manager...", color='CYAN')
        # Clear lease log
        if Path('/var/lib/misc/dnsmasq.leases').is_file():
            Console.info("Clearing leases file...")
            sudo_writefile('/var/lib/misc/dnsmasq.leases', "\n")

        # If nohup is true, do not restart dhcpcd
        if not nohup:
            Console.info("Restarting dhcpcd please wait...")

            status = cls._system('sudo service dhcpcd restart', exitcode=True)
            if status != 0:
                Console.error(
                    f'Did not restart manager networking service correctly')
                sys.exit(1)
            Console.info("Restarted dhcpcd")
            Console.info("Verifying dhcpcd status...")
            # Give the service a change to adjust
            time.sleep(2)
            if not cls._dhcpcd_active(iface=priv_iface):
                Console.error(
                    'Timeout: Could not boot dhcpcd in the allotted amont of time. '
                    'Use `sudo service dhcpcd status` for more info.')
                sys.exit(1)

            Console.ok("Verified dhcpcd status successfuly")

        Console.info("Restarting dnsmasq please wait...")
        status = cls._system('sudo service dnsmasq restart', exitcode=True)
        if status != 0:
            Console.error(f'Did not restart manager dnsmasq service correctly')
            sys.exit(1)
        Console.ok("Restarted dnsmasq successfuly")

        Console.ok("Restarted bridge service on manager")

        if workers is not None:
            banner("Restart networking service on workers...", color='CYAN')
            ignore_setting = '-o "StrictHostKeyChecking no"'
            for worker in workers:
                Console.info(f"Restarting dhcpcd on {worker} please wait...")
                status = cls._system(
                    f'ssh {ignore_setting} {user}@{worker} sudo service dhcpcd restart',
                    exitcode=True)
                if status != 0:
                    Console.error(
                        f'Did not restart {worker} DHCP service correctly')
                    sys.exit(1)
                Console.ok(f"Restarted dhcpcd on {worker}")

            Console.ok("Restarted DHCP service on workers")

    @classmethod
    def info(cls):
        try:
            info = readfile('~/.cloudmesh/bridge/info').split('\n')
            info = info[:info.index(cls.lease_bookmark) + 1]
        except Exception as e:
            Console.error(
                "Cannot execute info command. Has the bridge been made yet?")
            sys.exit(1)

        try:
            curr_leases = sudo_readfile('/var/lib/misc/dnsmasq.leases')
            # If cur_leases is not empty, then the first element of each row is the epoch time of
            # the lease expiration date
            for i in range(len(curr_leases)):
                curr_leases[i] = curr_leases[i].split()
                curr_leases[i][0] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.localtime(
                                                      int(curr_leases[i][0])))
                curr_leases[i] = ' '.join(curr_leases[i])

            curr_leases = '\n' + '\n'.join(curr_leases)

        except Exception as e:
            Console.warning(
                "dnsmasq.leases file not found. No devices have been connected yet")
            curr_leases = "\n"

        toWrite = '\n'.join(info) + curr_leases
        sudo_writefile('~/.cloudmesh/bridge/info', toWrite)

        banner(toWrite, color='CYAN')

    # Begin private methods for Bridge
    @classmethod
    def _system(cls, command, exitcode=False, warnuser=True, both=False):
        """
        :param command:
        :param exitcode: True if we only want exitcode
        :param warnuser: True if we want to warn the user of command errors
        :param both: True if we want both the exit code and the stdout. Takes precedent over exitcode
        :return: stdout of command
        """
        exit, stdout = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        if exit != 0 and warnuser:
            Console.warning(
                f'Warning: "{command}" did not execute properly -> {stdout} :: exit code {exit}')
        if both:
            return exit, stdout
        elif exitcode:
            return exit
        else:
            return stdout

    @classmethod
    def _dhcpcd_active(cls, iface='eth0', timeout=10, time_interval=5):
        """
        Returns True if dhcpcd is active else False

        :param iface: the interface that is connected to the private network. Default eth0
        :return boolean:
        """
        # It's possible dhcpcd isn't fully started up yet after restarting.
        # This is tricky as it says active even if it may fail
        # after probing all interfaces
        # Usually, dhcpcd is working once we see
        # f'{interface}: no IPv6 Routers available' somewhere in the status message
        pattern = re.compile(f'{iface}: no IPv6 Routers available*')

        # Loop if necessary
        restartCount = 1
        count = 1
        while True:
            Console.info(f'Checking if dhcpcd is up - Attempt {count}')
            code, full_status = cls._system('sudo service dhcpcd status',
                                            warnuser=False, both=True)
            if pattern.search(full_status):
                Console.info('dhcpcd is done starting')
                status_line = cls._system(
                    'sudo service dhcpcd status | grep Active')
                return 'running' in status_line

            # Occassionally dhcpcd fails to start when using WiFi. 
            # Unresolved bug as it works after a few restarts
            elif code != 0:
                if restartCount >= 5:
                    return False
                else:
                    Console.warning(
                        f'dhcpcd failed to restart. Retrying in 5 seconds... '
                        f'Restart number {restartCount} - Maximum 5 restarts')
                    time.sleep(time_interval)
                    cls._system('sudo service dhcpcd restart')
                    restartCount += 1
                    count = 1
                    continue

            if count >= timeout:
                status_line = cls._system(
                    'sudo service dhcpcd status | grep Active')
                return 'running' in status_line
            count += 1
            Console.info('dhcpcd is not ready. Checking again in 5 seconds...')
            time.sleep(time_interval)

    @classmethod
    def _convert_ipv4(cls, ip):
        """
        :param ip: An iPv4 address given as a string
        :return: tuple where the elements are the dot separated numerics of the ip
        """
        return tuple(int(n) for n in ip.split('.'))

    @classmethod
    def _in_range(cls, ip):
        """
        :param ip: An iPv4 address given as a string
        :return: True if the iPv4 is within cls.ip_range
        """
        return cls._convert_ipv4(cls.ip_range[0]) <= cls._convert_ipv4(
            ip) <= cls._convert_ipv4(cls.ip_range[1])

    @classmethod
    def _completion_message(cls):
        """
        Conveniently displays relevant information about this new bridge to the user as well as relevant commands

        :return:
        """
        info = textwrap.dedent(f"""
        IP range: {cls.ip_range[0]} - {cls.ip_range[1]}
        Manager IP: {cls.masterIP}

        {cls.lease_bookmark}

        """)

        banner(f"""
        Successfuly configured an internet bridge on this pi. Please reboot 
        for changes to take effect.
        
        Details:
          * This bridge will allow devices with ip in the {cls.masterIP}/24 
            range to connect to the internet through this pi
          * Manager Pi has ip {cls.masterIP} on interface {cls.priv_interface}
        """, color='CYAN')

        cls._system('sudo mkdir -p ~/.cloudmesh/bridge')
        sudo_writefile('~/.cloudmesh/bridge/info', info)

    @classmethod
    def _config_dnsmasq(cls):
        """
        Configure /etc/dnsmasq.conf to work as a dhcp server with the given IP range

        :return:
        """

        if cls.dryrun:
            Console.info("Writing dnsmasq config")
        else:
            Console.info("Configuring dnsmasq...")
            config = textwrap.dedent(f"""
            interface = {cls.priv_interface}
            listen-address={cls.masterIP}

            dhcp-range={cls.ip_range[0]},{cls.ip_range[1]},{cls.lease}

            server={cls.dns[0]}
            server={cls.dns[1]}

            bind-interfaces

            """)

            Console.info("Rewriting /etc/dnsmasq.conf")
            sudo_writefile('/etc/dnsmasq.conf', config)

            # Also add sleep 10 to /etc/init.d/dnsmasq so that it waits for dhcp to start

            initFile = sudo_readfile('/etc/init.d/dnsmasq')
            if 'sleep 10' not in initFile:
                temp = ['sleep 10']
                temp += initFile
                # The first line in initFile is #!/bin/sh
                # Move it to index 0 of temp
                temp[0], temp[1] = temp[1], temp[0]
                sudo_writefile('/etc/init.d/dnsmasq', '\n'.join(temp) + '\n')

    @classmethod
    def _install_dnsmasq(cls):
        """
        Uses apt-get to install package dnsmasq

        :return:
        """
        if cls.dryrun:
            Console.info('Installing dnsmasq...')
        else:
            banner("""

            Installing dnsmasq. Please wait for installation to complete. 

            """)

            StopWatch.start('install dnsmasq')
            # cls._system(f'sudo apt-get install -y dnsmasq')
            # Use os.system to display the installation feedback
            os.system('sudo apt-get install -y dnsmasq')
            StopWatch.stop('install dnsmasq')
            StopWatch.status('install dnsmasq', True)

            Console.ok("Finished installing dnsmasq")

    @classmethod
    def _purge_dnsmasq(cls):
        """
        Uses apt-get remove along with --purge and --auto-remove to remove dnsmasq.
        """
        Console.info("Purging dnsmasq. Please wait...")
        # cls._system('sudo apt-get --purge --auto-remove remove -y dnsmasq', warnuser=False)
        # We use os.system this time so that we can display the output as it is purged.
        os.system('sudo apt-get --purge --auto-remove remove -y dnsmasq')
        Console.info("Removed dnsmasq")

    @classmethod
    def _dnsmasq_exists(cls):
        """
        Returns true if dnsmasq service is already installed
        """
        exitCode, status = cls._system("dpkg-query -W -f='${Status}' dnsmasq",
                                       warnuser=False, both=True)
        if exitCode != 0:
            return False
        return status == 'install ok installed'

    @classmethod
    def _dhcpcd_conf(cls):
        """
        Configures manager with static ip masterIP on interface priv_interface in dhcpcd.conf.
        Considered as the IP address of the "default gateway" for the cluster network
        Note: Does not restart dhcpcd.service

        :return:
        """
        if cls.dryrun:
            Console.info(
                f"DRYRUN: Setting ip on {cls.priv_interface} to {cls.masterIP}")
        else:
            banner(f"""
            
            Writing to dhcpcd.conf. Setting static IP of manager to {cls.masterIP} on {cls.priv_interface}

            """)

            iface = f'interface {cls.priv_interface}'
            static_ip = f'static ip_address={cls.masterIP}'

            curr_config = sudo_readfile('/etc/dhcpcd.conf')
            if iface in curr_config:
                Console.warning("Found previous settings. Overwriting")
                # If setting already present, replace it and the static ip line
                index = curr_config.index(iface)
                try:
                    if 'static ip_address' not in curr_config[index + 1]:
                        Console.warning(
                            "Missing static ip_address assignment. Overwriting line")
                    curr_config[index + 1] = static_ip

                except IndexError:
                    Console.error('/etc/dhcpcd.conf ends abruptly. Aborting')
                    sys.exit(1)

            else:
                curr_config.append(iface)
                curr_config.append(static_ip)
                curr_config.append('nolink\n')

            sudo_writefile('/etc/dhcpcd.conf', '\n'.join(curr_config))
            Console.ok('Successfully wrote to /etc/dhcpcd.conf')

    @classmethod
    def _set_ipv4(cls):
        """
        Turns on iPv4 Forwarding on the system
        and saves rules upon eventual reboot

        :return:
        """
        if cls.dryrun:
            Console.info("DRYRUN: Turning on iPv4")
        else:
            new_line = 'net.ipv4.ip_forward=1'

            # First turn on ipv4 forwarding
            cls._system(f'sudo sysctl -w {new_line}')

            # Save for next boot
            old_conf = sudo_readfile('/etc/sysctl.conf')

            if new_line not in old_conf:
                # The default sysctl has the new_line commented out. Try to uncomment it
                try:
                    old_conf[old_conf.index('#' + new_line)] = new_line
                except ValueError:
                    Console.warning(
                        "Could not find iPv4 setting. Perhaps /etc/sysctl.conf "
                        "has been changed from default. Process continues by adding iPv4 setting")
                    old_conf.append('net.ipv4.ip_forward=1')
                except Exception as e:
                    Console.error(
                        "Could not set iPv4 forwarding. Unknown error occurred")
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
        cmd2 = f"sudo iptables -A FORWARD -i {cls.ext_interface} -o {cls.priv_interface}"\
               " -m state --state ESTABLISHED,RELATED -j ACCEPT"
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
                Console.error(
                    'rc.local does not have exit 0 in last line. '
                    'Contingency not handled in this version. '
                    'Cannot enable iPv4 forwarding at this time')
                raise NotImplementedError

            if restore_command not in old_conf:
                old_conf.append(restore_command)
                old_conf[-1], old_conf[-2] = old_conf[-2], old_conf[
                    -1]  # Places 'exit 0' below our restore_command
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
            Console.info(
                f"scp /etc/network/interfaces from {cls.master} to {user}@{worker}")
            Console.info(
                "Configure default gateway and DNS for {cls.priv_interface} on {user}@{worker}")

        else:
            # Get gateway and netmask for worker
            conf = cls._system('ifconfig')
            conf = conf.split('\n')

            # Search for priv_interface
            info = None
            for i in range(len(conf)):
                if cls.priv_interface in conf[i]:
                    info = conf[i + 1].split()

            if info is None:
                Console.error(f"Interface {cls.priv_interface} not found")
                sys.exit(1)

            elif info[0] != 'inet':
                Console.error(
                    f"Interface {cls.priv_interface} found, but there appears to be no iPv4 connection")
                sys.exit(1)

            else:
                # info ex: ['inet', '192.168.1.34', 'netmask', '255.255.255.0', 'broadcast', '192.168.1.255']
                gateway = info[1]
                netmask = info[3]

                # Use scp to get /etc/network/interfaces from worker
                cls._system('mkdir -p ~/.cloudmesh/tmp')
                tmp = f'~/.cloudmesh/tmp/{worker}-interfaces.tmp'

                ignore_setting = '-o "StrictHostKeyChecking no"'
                StopWatch.start(f'Talking to {user}@{worker}')
                exit_code = cls._system(
                    f'scp {ignore_setting} {user}@{worker}:/etc/network/interfaces {tmp}',
                    exitcode=True)
                StopWatch.stop(f'Talking to {user}@{worker}')
                StopWatch.status(f'Talking to {user}@{worker}', exit_code == 0)

                # Write new interfaces file
                try:
                    interfaces = readfile(tmp).rstrip().split('\n')
                except Exception as e:
                    Console.error(f"Could not open {tmp}")
                    sys.exit(1)

                try:
                    ind = interfaces.index(f'auto {cls.priv_interface}')
                except Exception as e:
                    Console.error(
                        f"Could not find {cls.priv_interface} configuration in interfaces file")

                interface_config = [line.lstrip() for line in
                                    interfaces[ind: ind + 3]]
                interface_config.append(f'gateway {gateway}')
                interface_config.append(f'netmask {netmask}')
                dnss = " ".join(cls.dns) + "\n"
                interface_config.append(f'dns-nameservers {dnss}')

                new_config = interfaces[:ind] + interface_config
                writefile(tmp, '\n'.join(new_config))

                # New config file now written on local machine. Move to worker in tmp directory
                remote_cmd1 = 'mkdir -p ~/.cloudmesh/tmp'
                remote_path = '~/.cloudmesh/tmp/interface.tmp'
                cls._system(
                    f'ssh {ignore_setting} {user}@{worker} {remote_cmd1}')
                cls._system(
                    f'scp {ignore_setting} {tmp} {user}@{worker}:{remote_path}')
                remote_cmd2 = 'sudo cp ~/.cloudmesh/tmp/interface.tmp /etc/network/interfaces'
                cls._system(
                    f'ssh {ignore_setting} {user}@{worker} {remote_cmd2}')

# Tests
# Bridge.create(master='red', workers=['red001'], priv_interface='eth0', ext_interface='wlan0', dryrun=True)
# Bridge.restart(master='red', workers=['red001'])
# StopWatch.benchmark(sysinfo=False, csv=False, tag='Testing')
