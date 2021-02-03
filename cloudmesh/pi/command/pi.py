from __future__ import print_function

from getpass import getpass

from cloudmesh.pi.cluster.Installer import Script
from cloudmesh.common.console import Console
from cloudmesh.pi.board.free import Free
from cloudmesh.pi.board.led import LED
from cloudmesh.pi.board.load import Load
from cloudmesh.pi.board.temperature import Temperature
from cloudmesh.pi.wifi import Wifi
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class PiCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
        """
        ::

          Usage:
            pi led reset [NAMES]
            pi led (red|green) VALUE
            pi led (red|green) VALUE NAMES [--user=USER]
            pi led list NAMES [--user=USER]
            pi led blink (red|green) NAMES [--user=USER] [--rate=SECONDS]
            pi led sequence (red|green) NAMES [--user=USER] [--rate=SECONDS]
            pi temp NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
            pi free NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
            pi load NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
            pi script list SERVICE [--details]
            pi script list SERVICE NAMES
            pi script list
            pi wifi SSID [PASSWORD] [--dryrun]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file


          Description:

            This command switches on and off the LEDs of the specified PIs. If
            the hostname is ommitted. IT is assumed that the code is executed on
            a PI and its LED are set. To list the PIs LED status you can use the
            list command

            Examples:

                cms pi led list  "red,red[01-03]"

                    lists the LED status of the given hosts

                cms pi led red off  "red,red[01-03]"

                    switches off the led of the given PIs

                cms pi led red on  "red,red[01-03]"

                    switches on the led of the given PIs

                cms pi led red blink  "red,red[01-03]"

                    switches on and off the led of the given PIs

                cms pi led red sequence  "red,red[01-03]"

                    goes in sequential order and switches on and off the led of
                    the given PIs

        """

        map_parameters(arguments,
                       'details',
                       'master',
                       'workers',
                       'output',
                       'user',
                       'rate')

        arguments.output = arguments.output or 'table'

        if arguments.free:

            free = Free()
            free.execute(arguments)

        elif arguments.temp:

            temp = Temperature()
            temp.execute(arguments)

        elif arguments.load:

            load = Load()
            load.execute(arguments)

        elif arguments.led:

            led = LED()
            led.execute(arguments)

        elif arguments.script:

            script = Script()
            script.execute(arguments)

        elif arguments.wifi:

            wifi = Wifi()

            if not wifi.is_root():
                Console.error("You are not running in sudo")
                return ""

            if arguments.PASSWORD is None:
                arguments.PASSWORD = getpass(
                    f"Wifi Password for {arguments.SSID}: ")

            wifi.set(arguments.SSID, arguments.PASSWORD,
                     dryrun=arguments["--dryrun"])

        return ""
