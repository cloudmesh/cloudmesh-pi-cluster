import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.util import writefile
from cloudmesh.common.sudo import Sudo


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
    """)  # noqa: W293

    @staticmethod
    def set(ssid, password, location=None, sudo=False, dryrun=False):
        location = location or Wifi.location

        if ssid is None or password is None:
            Console.error("SSID or password not set")
        if dryrun:
            password = "********"
        config = Wifi.template.format(**locals())
        if dryrun:
            print(location)
            print(config)
        else:
            try:
                if sudo:
                    Sudo.writefile(location, config)
                else:
                    writefile(location, config)

            except FileNotFoundError as e:  # noqa: F841
                Console.error(f"The file does not exist: {location}")
