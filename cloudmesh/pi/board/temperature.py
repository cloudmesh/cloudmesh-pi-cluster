import os
from cloudmesh.common.Host import Host
from pprint import pprint
import time
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Printer import Printer


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
        rate=None,
        processors=3,
        printer=None):

        command = "cat /sys/class/thermal/thermal_zone0/temp; /opt/vc/bin/vcgencmd measure_temp"

        printer = printer or pprint

        while True:

            result = Temperature.get(
                hosts=hosts,
                username=username,
                key="~/.ssh/id_rsa.pub",
                processors=3)

            printer(result)
            if rate:
                time.sleep(rate)
            else:
                break
