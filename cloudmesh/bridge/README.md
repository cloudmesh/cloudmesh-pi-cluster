# A simple command to setup a network bridge between raspberry pi workers and master
WARNING: This program is designed for Raspberry Pi and must not be executed on your laptop
---
# Quick Start
---
For reference, we will use the following setup:
* Master Pi hostname is `red`
* Master Pi is connected to network switch via the build-in ethernet port on the Pi
* Master Pi is connected to the internet via interface `wlan0` (WiFi)
* Master Pi is running the most up-to-date raspbian
* Master Pi has installed the necessary cloudmesh pi programs and burned three workers utilizing cm-pi-burn. See [cloudmesh-pi-burn](https://github.com/cloudmesh/cloudmesh_pi_burn/blob/master/cmburn/pi/README.md) for details.
* 3 worker Pis burned with hostnames `red001, red002, red003` with ipaddresses `169.254.10.1, 169.254.10.2, 169.254.10.3` respectively.

---
We can configure our network bridge as follows:
```
(ENV3) pi@red:$ cms bridge create red,red[001-003] --interface='wlan0'
```

Wait for the program to finish. If no errors, occured, we have successfuly configured the bridge.


To see changes take effect, simply restart your interfaces as follows:
```
(ENV3) pi@red:$ cms bridge restart red,red[001-003]
```

To test connections, utilize ssh to connect to you workers. There are several tests you can run to verify a connection. A simple way is:
```
pi@red001:$ sudo apt-get update
```
or
```
pi@red001:$ ping google.com
```
(hint: use ctrl+c to stop ping command)


In the future, we will automate these tests in the form:
```
(ENV3) pi@red:$ cms bridge test red,red[001-003]
```


