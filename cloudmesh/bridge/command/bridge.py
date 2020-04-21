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
            bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE]
            bridge set HOSTS ADDRESSES 
            bridge restart [--workers=WORKERS] 
            bridge test NAMES [--rate=RATE]
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

            bridge restart [--workers=WORKERS]
                restarts the bridge on the master without rebooting. 
                If --workers is specified, restart the interfaces on
                the workers via ssh.

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
                       'workers')

        if arguments.set:
            StopWatch.start('Static IP assignment')

            addresses = Parameter.expand(arguments.ADDRESSES)
            hosts = Parameter.expand(arguments.HOSTS)
            Bridge.set(workers=hosts, addresses=addresses)
            banner(f"""
            You have successfuly set static ip(s) for
            {arguments.HOSTS} with ips {arguments.ADDRESSES}

            To see changes on server, run:

            $ cms bridge restart

            If {arguments.HOSTS} is connected already, 
            restart bridge then reboot {arguments.HOSTS}.

            """, color='CYAN')

            StopWatch.stop('Static IP assignment')
            StopWatch.status('Static IP assignment', True)


        elif arguments.create:
            StopWatch.start('Bridge Creation')

            Bridge.create(masterIP=arguments.ip, ip_range=arguments.range.split("-"), priv_interface='eth0', ext_interface=arguments.interface)

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

            banner("test")

        elif arguments.restart:
            StopWatch.start('Network Service Restart')
            workers = Parameter.expand(arguments.workers)
            Bridge.restart(workers=workers)
            StopWatch.stop('Network Service Restart')
            StopWatch.status('Network Service Restart', True)

        elif arguments.list:

            banner("list")

        elif arguments.check:

            banner("check")

        StopWatch.stop('command')
        StopWatch.status('command', True)
        StopWatch.benchmark(sysinfo=False, csv=False)
        return ""
