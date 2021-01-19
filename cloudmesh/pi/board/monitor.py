import os
import time
from itertools import count
from pprint import pprint

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from cloudmesh.common.Host import Host
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.parameter import Parameter
from matplotlib.animation import FuncAnimation
from cloudmesh.common.debug import VERBOSE


class Monitor:

    def __init__(self):
        self.order = None
        self.title = "Monitor"

    def execute(self, arguments):

        if type(arguments.NAMES) != list:
            arguments.NAMES = list(Parameter.expand(arguments.NAMES))

        if arguments.rate and arguments.output == 'graph':

            self.WatchGraph(arguments.NAMES)

        elif arguments.rate:

            results = self.watch(
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=float(arguments.rate),
                processors=3,
                output=arguments.output
            )

        else:

            results = self.get(
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3,
            )

            if arguments.output in ['bar', 'browser', 'sparkline', 'line']:
                self.Graph(results, output=arguments.output)
            else:
                self.Print(results, output=arguments.output)

    def update(self, entry, table=None):
        return entry

    def Print(self, results, output=None):

        output = output or 'table'

        if output == 'table':
            for result in results:
                result = self.update(result, table=True)
            print(Printer.write(results, order=self.order))
        else:
            pprint(results)

    def get(self,
            hosts=None,
            username=None,
            key="~/.ssh/id_rsa.pub",
            processors=3,
            update=None,
            ):

        results = Host.ssh(hosts=hosts,
                           command=self.command,
                           username=username,
                           key="~/.ssh/id_rsa.pub",
                           processors=processors,
                           executor=os.system)

        for entry in results:
            entry = self.update(entry)

        return results

    def watch(self,
              hosts=None,
              username=None,
              key="~/.ssh/id_rsa.pub",
              rate=3.0,
              processors=3,
              output=None,
              ):

        output = output or 'table'

        try:

            while True:

                result = self.get(
                    hosts=hosts,
                    username=username,
                    key="~/.ssh/id_rsa.pub",
                    processors=3,
                )

                os.system('clear')
                self.Print(result, output=output)
                print()
                print("Press CTRL-C to end")
                if rate:
                    time.sleep(rate)
                else:
                    break
        except KeyboardInterrupt:
            print()
            print("Terminating, please wait ...")
            print()

    def WatchGraph(self,
                   hosts=None,
                   username=None,
                   key="~/.ssh/id_rsa.pub",
                   rate=3.0,
                   processors=3,
                   output=None):

        series = {}
        for host in hosts:
            series[host] = {'x': []}
            for attribute in self.display:
                series[host][attribute] = []

        index = count()

        output = output or 'table'

        plt.style.use('seaborn')

        fig, axs = plt.subplots(len(hosts),
                                1,
                                sharex=True,
                                sharey=True)

        fig.suptitle(f'Pi Cluster {self.title}')

        def animate(i):

            results = self.get(
                hosts=hosts,
                username=username,
                key="~/.ssh/id_rsa.pub",
                processors=3)

            plt.cla()

            host_no = 0

            i = next(index)

            for result in results:
                host = result['host']

                series[host]['x'].append(i)
                for attribute in self.display:
                    series[host][attribute].append(result[attribute])

                for attribute in self.display:
                    if len(hosts) == 1:
                        axs.plot(series[host]['x'],
                                 series[host][attribute],
                                 color=self.color[attribute],
                                 label=attribute)

                    else:
                        axs[host_no].plot(series[host]['x'],
                                          series[host][attribute],
                                          color=self.color[attribute],
                                          label=attribute)
                patches = []
                for attribute in self.display:
                    patch = mpatches.Patch(color=self.color[attribute],
                                           label=attribute)
                    patches.append(patch)
                if len(hosts) == 1:
                    axs.legend(handles=patches)
                    axs.set_title(host, loc='right')
                else:
                    axs[host_no].legend(handles=patches)
                    axs[host_no].set_title(host, loc='right')

                host_no += 1

        try:

            print()
            print("To exit close the anmimation window")

            ani = FuncAnimation(plt.gcf(), animate, int(rate * 1000))

            plt.tight_layout()
            plt.show()

        except KeyboardInterrupt:
            print()
            print("Terminating, please wait ...")
            print()
