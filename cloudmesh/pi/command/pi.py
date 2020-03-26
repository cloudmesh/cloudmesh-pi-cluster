from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.pi.board.led import LED
from cloudmesh.shell.command import map_parameters

class PiCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
        """
        ::

          Usage:
                pi led (red|green) VALUE
                pi led (red|green) VALUE NAMES [--user=USER]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """

        map_parameters(arguments,
                       'user')

        if not arguments.NAMES:
            if arguments.led and arguments.red:
                LED.set(led=1, value=arguments.VALUE)
            elif arguments.led and arguments.green:
                LED.set(led=0, value=arguments.VALUE)
        else:
            LED.set_remote(arguments.NAMES,
                           arguments.user)

        return ""
