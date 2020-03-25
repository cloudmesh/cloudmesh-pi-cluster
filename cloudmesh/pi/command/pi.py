from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.pi.board.led import LED

class PiCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
        """
        ::

          Usage:
                pi led (red|green) NAMES VALUE

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
        if arguments.led and arguments.red:
            print ("red")
            #LED.set(1, arguments.VALUE)
        elif arguments.led and arguments.green:
            print ("green")

            #LED.set(0, arguments.VALUE)


        return ""
