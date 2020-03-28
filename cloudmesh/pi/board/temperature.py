import os
from cloudmesh.common.Host import Host
from pprint import pprint
import time
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Printer import Printer
import sys

class Temperature:

    @staticmethod
    def Print(results, output=None):

        output = output or 'table'

        if output == 'table':
            print(Printer.write(results,
             order=['host', 'cpu', 'gpu']))
        else:
            pprint(results)

    @staticmethod
    def get(
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        processors=3):

        hosts = Parameter.expand(hosts)

        command = "cat /sys/class/thermal/thermal_zone0/temp; /opt/vc/bin/vcgencmd measure_temp"

        results = Host.ssh(hosts=hosts,
                          command=command,
                          username=username,
                          key="~/.ssh/id_rsa.pub",
                          processors=processors,
                          executor=os.system)
        for entry in results:
            cpu, gpu = entry["stdout"].splitlines()
            entry["gpu"] = gpu.split("=",1)[1][:-2]
            entry["cpu"] = float(cpu) / 1000.0

        return results

    @staticmethod
    def watch(
        hosts=None,
        username=None,
        key="~/.ssh/id_rsa.pub",
        rate=3.0,
        processors=3,
        output=None):

        command = "cat /sys/class/thermal/thermal_zone0/temp; /opt/vc/bin/vcgencmd measure_temp"

        output = output or 'table'

        try:

            while True:

                result = Temperature.get(
                    hosts=hosts,
                    username=username,
                    key="~/.ssh/id_rsa.pub",
                    processors=3)

                os.system('clear')
                Temperature.Print(result, output=output)
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