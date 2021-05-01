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
from cloudmesh.pi.nfs.Nfs import Nfs


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
            pi temp NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
            pi free NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
            pi load NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
            pi wifi SSID [PASSWORD] [--dryrun]
            pi script list SERVICE [--details]
            pi script list SERVICE NAMES
            pi script list
            pi nfs install
            pi nfs uninstall
            pi nfs share --paths=PATHS --hostnames=HOSTNAMES
            pi nfs unshare --path=PATH --hostnames=HOSTNAMES [--terminate]


          Arguments:
              NAMES       The hostnames in parameterized form
              VALUE       The Values are on, off, 0, 1
              USER        The user name for a login
              SSID        The ssid of your WIfi
              PASSWORD    The password for the WIFI

            Options:
               -v               verbose mode
               --output=OUTPUT  the format in which this list is given
                                formats includes cat, table, json, yaml,
                                dict. If cat is used, it is just print
               --user=USER      the user name
               --rate=SECONDS   repeats the quere given by the rate in seconds
               --hostnames=HOSTNAMES  hostnames for clients and optionally the server
               --manager=MANAGER  hostname for the server

          Description:

                This command allows to set the leds on the PI board and return
                information about the PIs such as temperature, memory space and
                load. It also allows to set the wifi for the PI.

                The most important part of this command is that it executes it not
                only on ome pi but multiple. The hostnames are defined by a parameterized
                notation. red0[1-2] results in red01 and red02.

                The script command are not yet completed and is under development

                The script commands can be used as an alternative to shell scripts.
                They are predefined scripts that can be run easily vai the command
                The script commands are listing details. This is useful as they are
                distributed with the cloudmesh shell. Thus no additional files are
                needed.

                At this time we do not define any predefined scripts.


            Examples:

                This command switches on and off the LEDs of the specified
                PIs. If the hostname is omitted. It is assumed that the
                code is executed on a PI and its LED are set. To list the
                PIs LED status you can use the list command

                cms pi led list  "red,red[01-03]"

                    lists the LED status of the given hosts

                cms pi led red off  "red,red[01-03]"

                    switches off the led of the given PIs

                cms pi led red on  "red,red[01-03]"

                    switches on the led of the given PIs

                cms pi led red blink  "red,red[01-03]"

                    switches on and off the led of the given PIs

                cms pi led red sequence  "red,red[01-03]"

                    goes in sequential order and switches on and off
                    the led of the given PIs

                To showcase information about temperature free space an load
                you can ues

                    pi temp "red,red[01-03]"
                    pi free "red,red[01-03]"
                    pi load "red,red[01-03]"

                To set the WIFI use (where SSID is your ssid). The command
                requires a reboot to activate the WIfi.

                    pi wifi SSID

                The script commands are not yet implemented

                    pi script list SERVICE [--details]
                    pi script list SERVICE NAMES
                    pi script list

                pi nfs install --hostnames=HOSTNAMES [--manager=MANAGER]

                    Installs an NFS server on the pi cluster that
                    can be accessed from the workers. If manager is not
                    specified the first host in hostname is supposed to be
                    the manager. Multiple NFS servers in teh clusyter could exists.

                pi nfs register --hostnames=HOSTNAME --manager=MANAGER

                    registers to the given hostnames the manager

        """

        map_parameters(arguments,
                       'details',
                       'manager',
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

        elif arguments.nfs:
            nfs = Nfs()

            if arguments.info:
                nfs.info()

            if arguments.install:
                nfs.install()

            if arguments.share:
                nfs.share(arguments['--paths'],arguments['--hostnames'])

            if arguments.unshare:
                if arguments.terminate:
                    nfs.unshare(arguments['--path'],arguments['--hostnames'],terminate = True)
                else:
                    nfs.unshare(arguments['--path'],arguments['--hostnames'])
                
        return ""
