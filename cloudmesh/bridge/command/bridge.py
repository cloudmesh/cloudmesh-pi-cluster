from __future__ import print_function
import sys
import textwrap

from cloudmesh.common.util import banner
from cloudmesh.shell.command import PluginCommand 
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.bridge.Bridge import Bridge

class BridgeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_bridge(self, args, arguments):
        """
        ::

          Usage:
            bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE] [--purge]
            bridge set HOSTS ADDRESSES 
            bridge restart [--nohup]
            bridge status
            bridge test HOSTS [--rate=RATE]
            bridge list NAMES
            bridge check NAMES [--configuration] [--connection]
            bridge info

          Arguments:
              HOSTS        Hostnames of connected devices. 
                           Ex. red002
                           Ex. red[002-003]
              
              ADDRESSES    IP addresses to assign to HOSTS. Addresses
                           should be in the network range configured.
                           Ex. 10.1.1.2
                           Ex. 10.1.1.[2-3]

              NAMES        A parameterized list of hosts. The first hostname 
                           in the list is the master through which the traffic 
                           is routed. Example:
                           blue,blue[002-003]

          Options:
              --interface=INTERFACE  The interface name [default: eth1]
                                     You can also specify wlan0 if you wnat
                                     to bridge through WIFI on the master
                                     eth0 requires a USB to WIFI adapter

              --ip=IPADDRESS         The ip address [default: 10.1.1.1] to assign the master on the
                                     interface. Ex. 10.1.1.1

              --range=IPRANGE        The inclusive range of IPs [default: 10.1.1.2-10.1.1.122] that can be assigned 
                                     to connecting devices. Value should be a comma
                                     separated tuple of the two range bounds. Should
                                     not include the ip of the master
                                     Ex. 10.1.1.2-10.1.1.20
              
              --workers=WORKERS      The parametrized hostnames of workers attatched to the bridge.
                                     Ex. red002
                                     Ex. red[002-003]

              --purge       Include option if a full reinstallation of dnsmasq is desired

              --nohup      Restarts only the dnsmasq portion of the bridge. This is done to surely prevent SIGHUP if using ssh.

              --rate=RATE            The rate in seconds for repeating the test
                                     If ommitted its done just once.

          Description:

            Command used to set up a bride so that all nodes route the traffic
            trough the master PI.

            bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE]
                creates the bridge on the current device
                The create command does not restart the network.

            bridge set HOSTS ADDRESSES 
                the set command assigns the given static 
                ip addresses to the given hostnames.

            bridge status
                Returns the status of the bridge and its linked services.

            bridge restart [--nohup]
                restarts the bridge on the master without rebooting. 

            bridge test NAMES
                A test to see if the bridges are configured correctly and one
                hase internet access on teh specified hosts.

            bridge list NAMES
                Lists information about the bridges (may not be needed)

            bridge check NAMES [--config] [--connection]
                provides information about the network configuration
                and netwokrk access. Thisis not a comprehensive speedtest
                for which we use test.

            bridge info
                prints relevant information about the configured bridge


          Design Changes:
            We still may need the master to be part of other commands in case
            for example the check is different for master and worker

        """

        map_parameters(arguments,
                       'interface',
                       'ip',
                       'range',
                       'workers',
                       'purge',
                       'nohup')

        if arguments.set:
            StopWatch.start('Static IP assignment')

            addresses = Parameter.expand(arguments.ADDRESSES)
            hosts = Parameter.expand(arguments.HOSTS)
            Bridge.set(workers=hosts, addresses=addresses)
            banner(f"""
            You have successfuly set static ip(s) for
            {arguments.HOSTS} with ips {arguments.ADDRESSES}

            To see changes on server, run:

            $ cms bridge restart --nohup

            If {arguments.HOSTS} is connected already, 
            restart bridge then reboot {arguments.HOSTS}.

            """, color='CYAN')

            StopWatch.stop('Static IP assignment')
            StopWatch.status('Static IP assignment', True)

        elif arguments.status:
            StopWatch.start('Status')
            Bridge.status()
            StopWatch.stop('Status')

        elif arguments.create:
            StopWatch.start('Bridge Creation')

            Bridge.create(masterIP=arguments.ip, ip_range=arguments.range.split("-"), priv_interface='eth0', ext_interface=arguments.interface, purge=True if arguments.purge else False)

            StopWatch.stop('Bridge Creation')
            StopWatch.status('Bridge Creation', True)
            banner(textwrap.dedent(f"""
            You have now configured a bridge on your master pi. To see the changes reflected, run the following command:

            cms bridge restart 

            """), color='CYAN')

        elif arguments.info:
            StopWatch.start('info')
            Bridge.info()
            StopWatch.stop('info')
            StopWatch.status('info', True)

        elif arguments.test:
            StopWatch.start('test')
            hosts = Parameter.expand(arguments.HOSTS)
            banner("Test command", color='CYAN')
            Bridge.test(hosts)
            StopWatch.stop('test')
            StopWatch.status('test', True)

        elif arguments.restart:
            StopWatch.start('Network Service Restart')
            workers = Parameter.expand(arguments.workers)
            nohup = True if arguments.nohup else False
            Bridge.restart(workers=workers, nohup=nohup)
            StopWatch.stop('Network Service Restart')
            StopWatch.status('Network Service Restart', True)

        elif arguments.list:

            banner("list")

        elif arguments.check:
            banner('Check')

        StopWatch.stop('command')
        StopWatch.status('command', True)
        StopWatch.status('load', True)
        # StopWatch.benchmark(sysinfo=False, csv=False)
        return ""
