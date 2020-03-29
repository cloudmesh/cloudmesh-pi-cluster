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

class Free:

    temp_min = 150.0
    temp_max = 0.0

    @staticmethod
    def Print(results, output=None):

        output = output or 'table'

        if output == 'table':
            print(Printer.write(results,
                  order=['host',
                         'mem.total', 'mem.used', 'mem.free', 'mem.shared',
                         'mem.cache', 'mem.avail',
                         'swap.total', 'swap.used', 'swap.free',
                         ]))
        else:
            pprint(results)

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

    @staticmethod
    def get(
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        processors=3):

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

        command = "free -b"

        results = Host.ssh(hosts=hosts,
                           command=command,
                           username=username,
                           key="~/.ssh/id_rsa.pub",
                           processors=processors,
                           executor=os.system)

        for entry in results:
            header, mem, swap = entry["stdout"].splitlines()

            data = mem.split()[1:6]
            entry['mem.total'], \
            entry['mem.used'], \
            entry['mem.free'], \
            entry['mem.shared'], \
            entry['mem.cache'], \
            entry['mem.avail'] = [humanize.naturalsize(v) for v in mem.split()[1:7]]
            entry['swap.total'], \
            entry['swap.used'], \
            entry['swap.free'] = [humanize.naturalsize(v) for v in swap.split()[1:4]]


        #
        #    cpu, gpu = entry["stdout"].splitlines()
        #   entry["gpu"] = float(gpu.split("=", 1)[1][:-2])
        #    entry["cpu"] = float(cpu) / 1000.0


        return results

    @staticmethod
    def watch(
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        rate=3.0,
        processors=3,
        output=None):

        output = output or 'table'

        try:

            while True:

                result = Free.get(
                    hosts=hosts,
                    username=username,
                    key="~/.ssh/id_rsa.pub",
                    processors=3)

                os.system('clear')
                Free.Print(result, output=output)
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

    @staticmethod
    def WatchGraph(
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        rate=3.0,
        processors=3,
        output=None):

        raise NotImplementedError

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
            series[host] = {'x': [], 'cpu': [], 'gpu': []}

        index = count()

        command = "cat /sys/class/thermal/thermal_zone0/temp; /opt/vc/bin/vcgencmd measure_temp"

        output = output or 'table'

        def animate(i):

            results = Temperature.get(
                hosts=hosts,
                username=username,
                key="~/.ssh/id_rsa.pub",
                processors=3)

            plt.cla()

            host_no = 0
            i = next(index)

            for result in results:
                host = result['host']
                gpu = result['gpu']
                cpu = result['cpu']

                Temperature.temp_min = min(gpu, cpu, Temperature.temp_min)
                Temperature.temp_max = max(gpu, cpu, Temperature.temp_max)

                series[host]['x'].append(i)
                series[host]['cpu'].append(cpu)
                series[host]['gpu'].append(gpu)
                axs[host_no].set_ylim([Temperature.temp_min, Temperature.temp_max])
                axs[host_no].plot(series[host]['x'], series[host]['cpu'], color='C0', label='cpu')
                axs[host_no].plot(series[host]['x'], series[host]['gpu'], color='C2', label='gpu')

                cpu_patch = mpatches.Patch(color='C0', label='CPU')
                gpu_patch = mpatches.Patch(color='C2', label='GPU')

                axs[host_no].legend(handles=[cpu_patch, gpu_patch])

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
