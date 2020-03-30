from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.pi.board.led import LED
from cloudmesh.pi.board.temperature import Temperature
from cloudmesh.pi.board.free import Free
from cloudmesh.pi.board.load import Load

from cloudmesh.shell.command import map_parameters
from cloudmesh.common.Printer import Printer


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
                pi spark setup --master=MASTER --workers=WORKER
                pi spark start --master=MASTER --workers=WORKER
                pi spark stop --master=MASTER --workers=WORKER
                pi spark test --master=MASTER --workers=WORKER
                pi spark check [--master=MASTER] [--workers=WORKER]

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

        elif arguments.spark:

            from cloudmesh.cluster.spark.spark import Spark
            spark = Spark()
            spark.execute(arguments)

        return ""
