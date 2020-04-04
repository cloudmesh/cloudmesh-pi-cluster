from __future__ import print_function

from cloudmesh.common.util import banner
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class BridgeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
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
              --rate                 The rate in seconds for repeating the test
                                     If ommitted its done just once.

          Description:

            Command used to set up a bride so that all nodes route the traffic
            trough the master PI.

            bridge create NAMES [--interface=INTERFACE]
                creates the bridge
                The set command does not restart the network.

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
            for example the check is different for master and worker.

        """

        map_parameters(arguments,
                       'interface')

        if arguments.set or arguments.create:
            master = arguments.NAMES[0]
            workers = arguments.NAMES[1:]
        else:
            hosts = arguments.NAMES

        if arguments.set:

            banner("set")

        elif arguments.create:

            banner("create")

        elif arguments.test:

            banner("test")

        elif arguments.restart:

            banner("restart")

        elif arguments.list:

            banner("list")

        elif arguments.check:

            banner("check")

        return ""
