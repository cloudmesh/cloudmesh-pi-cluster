# flake8: ignore=E127

import textwrap

from cloudmesh.bridge.Bridge import Bridge
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import banner
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class BridgeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_bridge(self, args, arguments):
        """
          Usage:
            bridge create [--interface=INTERFACE] [--ip=IP]

          Options:
              --interface=INTERFACE  The interface name [default: eth1]
                                     You can also specify wlan0 if you wnat
                                     to bridge through WIFI on the manager
                                     eth0 requires a USB to WIFI adapter

             --ip=IP  The ip address to assign on the eth0 interface,
                      ie. the listening interface [default: 10.1.1.1]

          Description:

            Command used to set up a bride so that all nodes route the traffic
            trough the manager PI.

            bridge create [--interface=INTERFACE] [--ip=IP]
                creates the bridge on the current device.
                A reboot is required.
        """

        map_parameters(arguments,
                       'interface',
                       'ip',
                       'range',
                       'workers',
                       'purge',
                       'nohup')

        if arguments.set:
            # StopWatch.start('Static IP assignment')

            # addresses = Parameter.expand(arguments.ADDRESSES)
            # hosts = Parameter.expand(arguments.HOSTS)
            # Bridge.set(workers=hosts, addresses=addresses)
            # banner(f"""
            # You have successfuly set static ip(s) for
            # {arguments.HOSTS} with ips {arguments.ADDRESSES}

            # To see changes on server, run:

            # $ cms bridge restart --nohup

            # If {arguments.HOSTS} is connected already,
            # restart bridge then reboot {arguments.HOSTS}.

            # """, color='CYAN')

            # StopWatch.stop('Static IP assignment')
            # StopWatch.status('Static IP assignment', True)
            print("Depcrecated Command. Needs Revisit")

        elif arguments.status:
            StopWatch.start('Status')
            # Bridge.status()
            StopWatch.stop('Status')
            print("Depcrecated Command. Needs Revisit")

        elif arguments.create:
            StopWatch.start('Bridge Creation')

            Bridge.create(managerIP=arguments.ip,
                          priv_interface='eth0',
                          ext_interface=arguments.interface)

            StopWatch.stop('Bridge Creation')
            StopWatch.status('Bridge Creation', True)
            banner(textwrap.dedent("""
            You have now configured a bridge on your manager pi.
            To see the changes reflected, please reboot.

            """), color='CYAN')

        elif arguments.info:
            StopWatch.start('info')
            # Bridge.info()
            StopWatch.stop('info')
            StopWatch.status('info', True)
            print("Depcrecated Command. Needs Revisit")

        elif arguments.test:
            # StopWatch.start('test')
            # hosts = Parameter.expand(arguments.HOSTS)
            # banner("Test command", color='CYAN')
            # Bridge.test(hosts)
            # StopWatch.stop('test')
            # StopWatch.status('test', True)
            print("Depcrecated Command. Needs Revisit")

        elif arguments.restart:
            # background = True if arguments.background else False
            # nohup = True if arguments.nohup else False
            # if background:
            #     if nohup:
            #         os.system(
            #             'nohup cms bridge restart --nohup > bridge_restart.log 2>&1 &')
            #     else:
            #         os.system(
            #             'nohup cms bridge restart > brige_restart.log 2>&1 &')

            # else:
            #     StopWatch.start('Network Service Restart')
            #     workers = Parameter.expand(arguments.workers)
            #     Bridge.restart(workers=workers, nohup=nohup)
            #     StopWatch.stop('Network Service Restart')
            #     StopWatch.status('Network Service Restart', True)
            print("Depcrecated Command. Needs Revisit")

        elif arguments.list:

            banner("list")

        elif arguments.check:
            banner('Check')

        StopWatch.stop('command')
        StopWatch.status('command', True)
        StopWatch.status('load', True)
        # StopWatch.benchmark(sysinfo=False, csv=False)
        return ""
