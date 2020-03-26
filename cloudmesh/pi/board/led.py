import os
from cloudmesh.common.Host import Host
from pprint import pprint
import time
from cloudmesh.common.parameter import Parameter

class LED:

    @staticmethod
    def set(led=None, value=1):
        if led not in [1, 0]:
            raise ValueError("Led number is wrong")
        state = value.lower() in ["1", "on", "true", "+"]
        if state:
            state = 1
        else:
            state = 0

        if led == 0:
            # switch it first off, technically we should disable the trigger first
            # then we do not have to switch it off
            command = f"echo 0 | sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"
            os.system(command)

        command = f"echo {state} | sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"

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
        state = value.lower() in ["1", "on", "true", "+"]
        if state:
            state = 1
        else:
            state = 0

        command = f"echo {state} | sudo tee /sys/class/leds/led{led}/brightness >> /dev/null"
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

        for i in range(0,3):
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

        command = f"cat /sys/class/leds/led0/brightness /sys/class/leds/led1/brightness"
        results = Host.ssh(hosts=hosts,
                          command=command,
                          username=username,
                          key="~/.ssh/id_rsa.pub",
                          processors=processors,
                          executor=os.system)
        for result in results:
            print (result)
            result["green"],result["red"] = result["stdout"].split("\n",1)

        return results
