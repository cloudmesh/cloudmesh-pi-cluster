import subprocess
import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.util import writefile


class Wifi:
    location = "/etc/wpa_supplicant/wpa_supplicant.conf"

    template = textwrap.dedent("""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US
        
        network={{
                ssid="{ssid}"
                psk="{password}"
                key_mgmt=WPA-PSK
        }}
    """)

    @staticmethod
    def set(ssid, password, dryrun=False):
        if ssid is None or password is None:
            Console.error("SSID or password not set")
        if dryrun:
            password = "********"
        config = Wifi.template.format(**locals()) \
            .replace("BEGIN", "{").replace("END", "}")
        if dryrun:
            print(Wifi.location)
            print(config)
        else:
            try:
                writefile(Wifi.location, config)
            except FileNotFoundError as e:
                Console.error(f"The file does not exist: {Wifi.location}")

    @staticmethod
    def is_root():
        username = subprocess.getoutput("whoami")
        return username == "root"
