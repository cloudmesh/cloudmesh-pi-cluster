## A simple command to setup a network bridge between raspberry pi workers and master utilizing dnsmasq
WARNING: This program is designed for Raspberry Pi and must not be executed on your laptop
---
##  Quick Start
---
For reference, we will use the following setup:
* Master Pi has hostname `red` and is connected to the internet via interface `wlan0` (WiFi)
* Master Pi is connected to network switch on `eth0` (private interface that workers will connect to)
* Cloudmesh is installed using `curl -Ls http://cloudmesh.github.io/get/pi | sh`
* Prior steps for `cms burn` [setup](https://github.com/cloudmesh/cloudmesh-pi-burn) are done
---
## Step 1. Create necessary workers
```
(ENV3) pi@red:$ cms burn create --hostname=red[001-003]
```
We do not need to boot them up yet as if we connect them to the master now, we will need to reboot them later. (It doesn't hurt though)

*Note* 
Notice how we are not setting the `--ipaddr` option. This is intentional as we want to handle static IPs in a centralized manner now. The program will still work if you configure the Pis with static IPs, but you just won't be able to change them from the master.

---

## Step 2.

We can configure our network bridge as follows:
```
(ENV3) pi@red:$ cms bridge create --interface='wlan0'
```

Wait for the program to finish. If no errors, occured, we have successfuly configured the bridge. Check details on the configuration using 
```
(ENV3) pi@red:$ cms bridge info
```

This will display the following important information (note this is the default setup):
```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.1 - 10.1.1.20
# Master IP: 10.1.1.0
# 
# # LEASES #
# ----------------------------------------------------------------------
```

The `Master IP` tells us the IP address of the master on the private interface (eth0).
The `IP Range` tells us the range of suitable IPs we can give to the workers.

In the future, a command will be added to expand the `IP range` dynamically.

## Step 3.

We can now restart the bridge to reflect these changes:
```
(ENV3) pi@red:$ cms bridge restart
```
This will allow us to immediately start connecting devices to our network switch and access the internet.

We can set a static IP for hostnames as follows:
```
(ENV3) pi@red:$ cms bridge set red001 10.1.1.1
(ENV3) pi@red:$ cms bridge set red[002-003] 10.1.1.[2-3]
```
We then restart the bridge again.
```
(ENV3) pi@red:$ cms bridge restart
```

*Note*
Any workers previously connected to the bridge that have just been assigned static IPs must be rebooted.

## Step 4.
To verify that workers have successfuly connected, we call the info command again:
```
(ENV3) pi@red:$ cms bridge info
```
In addition to the information displayed in step 2, we will also have information on the given leases below `# LEASES #` including the hostnames, MAC addresses, and the assigned IP.

## Step 5
Enjoy. These commands have been designed to prevent several user errors, and will most often have a handled error message for debugging purposes should any issues arise. Additionally, the above commands can be run as many times as needed. There should be no ill effects. 




*IMPORTANT NOTE*
When customizing the IP range of the server or setting static IPs, remember you must abide by RFC 1918 for Private addresses. The IP range must fall within one of the following ip ranges:
```
10.0.0.0        -   10.255.255.255  (10/8 prefix)
172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
192.168.0.0     -   192.168.255.255 (192.168/16 prefix)
```
The default configuration falls within the first of the listed ranges.
