from __future__ import print_function
import sys

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
            bridge create NAMES [--interface=INTERFACE]
            bridge set NAMES [--interface=INTERFACE]
            bridge restart NAMES 
            bridge test NAMES [--rate=RATE]
            bridge list NAMES
            bridge check NAMES [--configuration] [--connection]

          Arguments:
              NAMES  the parameterized list of the hosts to set up as the
                     bridge. The first hostname in the list is the master
                     through which the traffic is routed. Example:
                     red,red[01-03]
                     Only the set and create command require the master.

          Options:
              --interface=INTERFACE  The interface name [default: eth1]
                                     You can also specify wlan0 if you wnat
                                     to bridge through WIFI on the master
                                     eth0 requires a USB to WIFI adapter
              --rate=RATE            The rate in seconds for repeating the test
                                     If ommitted its done just once.

          Description:

            Command used to set up a bride so that all nodes route the traffic
            trough the master PI.

            bridge create NAMES [--interface=INTERFACE]
                creates the bridge
                The create command does not restart the network.

            bridge set NAMES [--interface=INTERFACE]
                sets the bridge if it is already created.
                The set command does not restart the network.

            bridge restart NAMES
                restarts the bridge interfaces without rebooting
                The network will be interrupted temporarily the command will
                wait till all pis come back.

            bridge test NAMES
                A test to see if the bridges are configured correctly and one
                hase internet access on teh specified hosts.

            bridge list NAMES
                Lists information about the bridges (may not be needed)

            bridge check NAMES [--config] [--connection]
                provides information about the network configuration
                and netwokrk access. Thisis not a comprehensive speedtest
                for which we use test.


          Design Changes:
            We still may need the master to be part of other commands in case
            for example the check is different for master and worker

        """

        map_parameters(arguments,
                       'interface')

        if arguments.set or arguments.create or arguments.restart:
            if ',' not in arguments.NAMES:
            # Handles either just master or just workers
                if arguments.create:
                    Console.warning("Creating bridge without workers. Only master will be configured")
                    master = arguments.NAMES
                    workers = None

                elif arguments.restart:
                    # Check whether the hostname(s) passed in is the master (this machine) or workers (remote machine)
                    try:
                        with open('/etc/hostname', 'r') as f:
                            thishost = f.read().strip()
                    except:
                        Console.error('Could not read /etc/hostname')
                        sys.exit(1)

                    if arguments.NAMES == thishost:
                        master = arguments.NAMES
                        workers = None
                    else:
                        workers = Parameter.expand(arguments.NAMES)
                        master = None

            else:
                master, workers = arguments.NAMES.split(',')
                workers = Parameter.expand(workers)
            
        else:
            hosts = arguments.NAMES

        if arguments.set:

            banner("set")

        elif arguments.create:
            StopWatch.start('Bridge Creation')
            Bridge.create(master=master, workers=workers, priv_interface='eth0', ext_interface=arguments.interface)
            StopWatch.stop('Bridge Creation')
            StopWatch.status('Bridge Creation', True)

        elif arguments.test:

            banner("test")

        elif arguments.restart:
            StopWatch.start('Network Service Restart')
            Bridge.restart(master=master, workers=workers)
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
