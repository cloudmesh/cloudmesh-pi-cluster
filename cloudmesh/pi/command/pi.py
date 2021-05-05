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
from cloudmesh.pi.cluster.k3.k3 import K3
from cloudmesh.pi.cluster.microk8s.microk8s import MicroK8s


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
            pi k3 enable containers NAMES
            pi k3 install server NAMES
            pi k3 install agent NAMES SERVER
            pi k3 install cluster NAMES
            pi k3 uninstall server NAMES
            pi k3 uninstall agent NAMES
            pi k3 uninstall cluster NAMES
            pi k3 kill NAMES
            pi k3 start server NAMES
            pi k3 start agent NAMES
            pi k3 start cluster NAMES
            pi k3 stop server NAMES
            pi k3 stop agent NAMES
            pi k3 stop cluster NAMES
            pi k3 remove node NAMES SERVER
            pi k3 cluster info SERVER
            pi k3 dashboard create SERVER
            pi k3 dashboard connect SERVER
            pi k3 dashboard disconnect [SERVER]
            pi k3 dashboard info
            pi k3 dashboard
            pi k3 import image NAMES SOURCE DESTINATION
            pi k3 api deploy SERVER PORTS YAML PYTHON
            pi microk8s install snapd NAMES
            pi microk8s install NAMES
            pi microk8s uninstall NAMES
            pi microk8s start NAMES
            pi microk8s stop NAMES
            pi microk8s inspect NAMES
            pi microk8s enable addon ADDONS NAMES
            pi microk8s cluster info SERVER
            pi microk8s join NAMES SERVER
            pi microk8s get node SERVER
            pi microk8s remove node NAMES
            pi script list SERVICE [--details]
            pi script list SERVICE NAMES
            pi script list

          Arguments:
              NAMES       The hostnames in parameterized form
              VALUE       The Values are on, off, 0, 1
              USER        The user name for a login
              SSID        The ssid of your WIfi
              PASSWORD    The assword for the WIFI

            Options:
               -v               verbose mode
               --output=OUTPUT  the format in which this list is given
                                formats includes cat, table, json, yaml,
                                dict. If cat is used, it is just print
               --user=USER      the user name
               --rate=SECONDS   repeats the quere given by the rate in seconds

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

        elif arguments.k3:
            k3 = K3()
            k3.execute(arguments)

        elif arguments.microk8s:
            microk8s = MicroK8s()
            microk8s.execute(arguments)

        return ""
