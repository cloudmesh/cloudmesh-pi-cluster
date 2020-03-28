from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.pi.board.led import LED
from cloudmesh.pi.board.temperature import Temperature
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.Printer import Printer


class PiCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
        """
        ::

          Usage:
                pi led (red|green) VALUE
                pi led (red|green) VALUE NAMES [--user=USER]
                pi led list NAMES [--user=USER]
                pi led blink (red|green) NAMES [--user=USER] [--rate=SECONDS]
                pi led sequence (red|green) NAMES [--user=USER] [--rate=SECONDS]
                pi temp NAMES [--watch] [--user=USER] [--output=FORMAT]

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
                       'output'
                       'user',
                       'watch')

        def _print(results):
            arguments.output = arguments.output or 'table'

            if arguments.output == 'table':
                print(Printer.write(results,
                                    order=['host', 'success', 'stdout']))
            else:
                pprint(results)

        def _print_leds(results):
            arguments.output = arguments.output or 'table'

            if arguments.output == 'table':
                print(Printer.write(results,
                                    order=['host', 'green', 'red']))
            else:
                pprint(results)

        if arguments.red:
            number = 1
        elif arguments.green:
            number = 0

        if arguments.temp and arguments.watch:
            results = Temperature.watch(
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=arguments.RATE,
                processors=3,
                output=arguments.output
            )

        if arguments.temp:

            results = Temperature.get(
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3,
            )

            Temperature.Print(results, output=arguments.output)

        elif arguments.sequence:

            results = LED.sequence_remote(
                led=number,
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=arguments.RATE,
                processors=3)

            _print_leds(results)

        elif arguments.blink:

            results = LED.blink_remote(
                led=number,
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=arguments.RATE,
                processors=3)

            _print_leds(results)

        elif arguments.list:

            results = LED.list_remote(
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3)

            _print_leds(results)

        elif not arguments.NAMES and arguments.led:

            LED.set(led=number, value=arguments.VALUE)

        elif arguments.NAMES and arguments.led:

            results = LED.set_remote(
                led=number,
                value=arguments.VALUE,
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3)

            _print(results)

        return ""
