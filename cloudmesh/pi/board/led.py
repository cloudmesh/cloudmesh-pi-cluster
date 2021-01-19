import os
import time
from pprint import pprint

from cloudmesh.common.Host import Host
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.parameter import Parameter

"""

From: https://www.raspberrypi.org/forums/viewtopic.php?t=12530

If you want the LED to go back to its default function:

echo mmc0 >/sys/class/leds/led0/trigger

As an aside, there are a couple of kernel modules you can load up (ledtrig_timer
and ledtrig_heartbeat) which will flash the LED for you.

modprobe ledtrig_heartbeat
echo heartbeat >/sys/class/leds/led0/trigger

Once you have turned off the mmc0 trigger, you can use GPIO16 to control the
LED. It's active-low, so you need to set the pin low to turn the LED on, and
high to turn it off.

"""


class LED:
    """
    Implements:

        pi led (red|green) VALUE
        pi led (red|green) VALUE NAMES [--user=USER]
        pi led list NAMES [--user=USER]
        pi led blink (red|green) NAMES [--user=USER] [--rate=SECONDS]
    """

    # TODO: implement: cms pi led reset  # to original setting
    # TODO: implement: cms pi led list --trogger list, list the triggers

    def __init__(self):
        pass

    def Print(self, arguments, results):

        if arguments.output == 'table':
            print(Printer.write(results,
                                order=['host', 'success', 'stdout']))
        else:
            pprint(results)

    def Print_leds(self, arguments, results):

        if arguments.output == 'table':
            print(Printer.write(results,
                                order=['host', 'green', 'red']))
        else:
            pprint(results)

    def execute(self, arguments):

        if arguments.red:
            arguments.number = 1
        elif arguments.green:
            arguments.number = 0

        if arguments.sequence:

            results = LED.sequence_remote(
                led=arguments.number,
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=arguments.RATE,
                processors=3)

            self.Print_leds(arguments, results)

        elif arguments.blink:

            results = LED.blink_remote(
                led=arguments.number,
                hosts=arguments.NAMES,
                username=arguments.user,
                rate=arguments.RATE,
                processors=3)

            self.Print_leds(arguments, results)

        elif arguments.list:

            results = LED.list_remote(
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3)

            self.Print_leds(arguments, results)

        elif arguments.reset and not arguments.NAMES and arguments.led:

            LED.reset()

        elif arguments.reset and arguments.NAMES and arguments.led:

            results = LED.reset_remote(
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3)

            self.Print(arguments, results)

        # elif not arguments.NAMES and arguments.led:

        #    LED.set(led=arguments.number, value=arguments.VALUE)

        elif arguments.NAMES and arguments.led:

            results = LED.set_remote(
                led=arguments.number,
                value=arguments.VALUE,
                hosts=arguments.NAMES,
                username=arguments.user,
                processors=3)

            self.Print(arguments, results)

    @staticmethod
    def get_state(value):
        state = value
        if type(value) == str:
            if value.lower() in ["1", "on", "true", "+"]:
                state = 1
            elif value.lower() in ["0", "off", "false", "-"]:
                state = 0
            else:
                state = int(value)

        return state

    @staticmethod
    def reset():

        command = f"echo mmc0 >/sys/class/leds/led0/trigger"
        os.system(command)

    @staticmethod
    def reset_remote(
            hosts=None,
            username=None,
            processors=3):

        command = f"echo mmc0 >/sys/class/leds/led0/trigger"
        result = Host.ssh(hosts=hosts,
                          command=command,
                          username=username,
                          key="~/.ssh/id_rsa.pub",
                          processors=processors,
                          executor=os.system)

    @staticmethod
    def set(led=None, value=1):

        if led not in [1, 0]:
            raise ValueError("Led number is wrong")

        state = LED.get_state(value)

        if led == 0:
            # switch it first off, technically we should disable the trigger
            # first
            # then we do not have to switch it off
            command = f"echo 0 | " \
                      "sudo tee /sys/class/leds/led{led}/brightness " \
                      ">> /dev/null"
            os.system(command)

        command = f"echo {state} | " \
                  "sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"

        os.system(command)

    @staticmethod
    def set_remote(
            led=None,
            value=1,
            hosts=None,
            username=None,
            processors=3):

        if led not in [1, 0]:
            raise ValueError("Led number is wrong")

        state = LED.get_state(value)

        command = f"echo {state} |" \
                  f" sudo tee /sys/class/leds/led{led}/brightness" \
                  f" >> /dev/null"
        print("command", command)
        result = Host.ssh(hosts=hosts,
                          command=command,
                          username=username,
                          key="~/.ssh/id_rsa.pub",
                          processors=processors,
                          executor=os.system)
        return result

    @staticmethod
    def blink_remote(
            led=None,
            hosts=None,
            username=None,
            rate=None,
            processors=3):

        if led not in [1, 0]:
            raise ValueError("Led number is wrong")
        rate = float(rate or 0.5)

        for i in range(0, 3):
            state = 0

            LED.set_remote(
                led=led,
                value="0",
                hosts=hosts,
                username=username,
                processors=processors)

            time.sleep(rate)

            LED.set_remote(
                led=led,
                value="1",
                hosts=hosts,
                username=username,
                processors=processors)

            time.sleep(rate)

        return None

    @staticmethod
    def sequence_remote(
            led=None,
            hosts=None,
            username=None,
            rate=None,
            processors=3):

        if led not in [1, 0]:
            raise ValueError("Led number is wrong")
        rate = float(rate or 0.5)

        hosts = Parameter.expand(hosts)
        for host in hosts:
            LED.set_remote(
                led=led,
                value="0",
                hosts=host,
                username=username,
                processors=processors)

            time.sleep(rate)

            LED.set_remote(
                led=led,
                value="1",
                hosts=host,
                username=username,
                processors=processors)

            time.sleep(rate)

        return None

    @staticmethod
    def list_remote(
            hosts=None,
            username=None,
            processors=3):

        command = f"cat" \
                  " /sys/class/leds/led0/brightness" \
                  " /sys/class/leds/led1/brightness"
        results = Host.ssh(hosts=hosts,
                           command=command,
                           username=username,
                           key="~/.ssh/id_rsa.pub",
                           processors=processors,
                           executor=os.system)
        for result in results:
            result["green"], result["red"] = result["stdout"].split("\n", 1)

        return results
