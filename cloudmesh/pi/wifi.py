import subprocess
import textwrap

from cloudmesh.common.console import Console


class Wifi:
    location = "/etc/wpa_supplicant/wpa_supplicant.conf"

    template = textwrap.dedent("""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US
        
        network=BEGIN
                ssid="{ssid}"
                psk="{password}"
                key_mgmt=WPA-PSK
        END
    """)

    @staticmethod
    def set(ssid, password):
        if ssid is None or password is None:
            Console.error("SSID or password not set")
        config = Wifi.template.format(**locals()).replace("BEGIN", "{").replace(
            "END", "}")
        # writefile(Wifi.location, config)
        print(Wifi.location)
        print(config)

    @staticmethod
    def is_root():
        username = subprocess.getoutput("whoami")
        return username == "root"
