import os
from cloudmesh.common.Host import Host
from pprint import pprint
import time
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Printer import Printer
import sys
import pygal
import webbrowser
from pygal.style import DefaultStyle
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import humanize
from cloudmesh.common.Printer import Printer

class Monitor:

    order = None
    value_min = sys.float_info.max
    value_max = sys.float_info.min

    def execute(self, arguments):

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

    def updat(self, entry):
        return entry

    def Print(self, results, output=None):

        output = output or 'table'

        if output == 'table':
            print(Printer.write(results, self.order))
        else:
            pprint(results)

    def get(self,
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        processors=3,
        update=None,
    ):

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

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

        if type(hosts) != list:
            hosts = list(Parameter.expand(hosts))

        plt.style.use('seaborn')

        fig, axs = plt.subplots(len(hosts))

        fig.suptitle('Pi Cluster Temperature')

        i = 0
        for host in hosts:
            axs[i].set_title(host, loc='left')
            i += 1

        series = {}
        for host in hosts:
            series[host] = {'x': []}
            for attribute in self.attributes:
                series[host][attribute] = []

        index = count()

        output = output or 'table'

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

                for attribute in self.attributes:
                    value = result[attribute]
                    self.value_min = min(value, self.value_min)
                    self.value_max = max(value, self.value_max)

                series[host]['x'].append(i)
                for attribute in self.attributes:
                    series[host][attribute].append(result[attribute])

                axs[host_no].set_ylim([self.value_min,
                                       self.value_max])
                for attribute in self.attributes:
                    axs[host_no].plot(series[host]['x'],
                                      series[host][attribute],
                                      color=self.color[attribute],
                                      label=attribute)

                patches = []
                for attribute in self.attributes:
                    patch = mpatches.Patch(color=self.color[attribute],
                                           label=attribute)
                    patches.append(patch)

                axs[host_no].legend(handles=patches)

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


    """
    @staticmethod
    def Graph(results, output='graph'):

        raise NotImplementedError

        cpu = [entry['cpu'] for entry in results]
        gpu = [entry['gpu'] for entry in results]
        host = [entry['host'] for entry in results]

        if output == 'line':
            chart = pygal.Line(
                title="Temperatures of the Pi Cluster",
                ymin=30, width=400, height=200,
                x_label_rotation=-45,
            )

        else:
            chart = pygal.Bar(
                title="Temperatures of the Pi Cluster",
                ymin=30, width=400, height=200,
                x_label_rotation=-45,
                print_values=True,
                print_values_position='top',
                style=DefaultStyle(
                    value_font_size=8,
                    value_colors=('black')
                )
            )

        chart.x_labels = host
        chart.add('CPU', cpu)
        chart.add('GPU', gpu)

        if output == 'browser':

            chart.render_in_browser(relative_to=50)

        elif output == 'sparkline':

            print(chart.render_sparktext(relative_to=50))

        elif output in ['bar', 'line']:

            chart.render_to_file('/tmp/chart.svg')
            webbrowser.open("file:///tmp/chart.svg")

        else:

            pprint(results)
    """