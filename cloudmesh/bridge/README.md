## A simple command to setup a network bridge between raspberry pi workers and master utilizing dnsmasq
WARNING: This program is designed for Raspberry Pi and must not be executed on your laptop
---
##  Quick Start
---
For reference, we will use the following setup:
* Master Pi has hostname `red` and is connected to the internet via interface `eth1` (usb -> ethernet) cable
* Master Pi is connected to network switch on `eth0` (private interface that workers will connect to ie. the hub). Make sure network switch is turned on.
* Cloudmesh is installed using `curl -Ls http://cloudmesh.github.io/get/pi | sh`
* If you choose to use WiFi `wlan0` I do not recommend using ssh to set this up as your ssh pipe may break on step 3 and you will need to wait for the command to complete before you are allowed back in. I recommend using a desktop setup in this case as the command will most likely result in an error.

---
## Step 1. Create necessary workers
Utilize [cmburn](https://github.com/cloudmesh/cloudmesh-pi-burn) to create the workers
```
(ENV3) pi@red:$ cms burn create --hostname=red[003-004]
```
Connect them to the private interface (network switch) via ethernet.

We do not need to boot them up yet as if we connect them to the master now, we will need to reboot them later. (It doesn't hurt though)

*Note* 
Notice how we are not setting the `--ipaddr` option. This is intentional as we want to handle static IPs in a centralized manner now. The program will still work if you configure the Pis with static IPs, but you just won't be able to change them from the master.

---

## Step 2 Create Bridge.
Plug the master Pi into the private interface (network switch) via the built-in ethernet port (eth0)

We can configure our network bridge as follows:
```
(ENV3) pi@red:$ cms bridge create --interface='eth1'
```

Wait for the program to finish. If no errors, occured, we have successfuly configured the bridge. Check details on the configuration using 
```
(ENV3) pi@red:$ cms bridge info
```

This will display the following important information (note this is the default setup):
```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.2 - 10.1.1.122
# Master IP: 10.1.1.1
# 
# # ACTIVE LEASES #
# ----------------------------------------------------------------------
```

The `Master IP` tells us the IP address of the master on the private interface (eth0).
The `IP Range` tells us the range of suitable IPs we can give to the workers.

In the future, a command will be added to expand the `IP range` dynamically.

---

## Step 3. Restart Bridge

We can now restart the bridge to reflect these changes:
```
(ENV3) pi@red:$ cms bridge restart
```
You will see output similar to the following:
```
INFO: Clearing leases file...
INFO: Restarting dhcpcd please wait...
INFO: Restarted dhcpcd
INFO: Verifying dhcpcd status...
INFO: Checking if dhcpcd is up - Attempt 1
INFO: dhcpcd is not ready. Checking again in 5 seconds
INFO: Checking if dhcpcd is up - Attempt 2
INFO: dhcpcd is not ready. Checking again in 5 seconds
INFO: Checking if dhcpcd is up - Attempt 3
INFO: dhcpcd is not ready. Checking again in 5 seconds
INFO: Checking if dhcpcd is up - Attempt 4
INFO: dhcpcd is done starting
Verified dhcpcd status successfuly
INFO: Restarting dnsmasq please wait...
Restarted dnsmasq successfuly
Restarted bridge service on master
```
* Note *

At this point, our bridge is ready and the master is configured with dhcp services.

---

## Step 4 (optional). Assign static IPs to workers
We can set a static IP for hostnames as follows:
```
(ENV3) pi@red:$ cms bridge set red003 10.1.1.3
```
for individual workers and/or
```
(ENV3) pi@red:$ cms bridge set red[003-004] 10.1.1.[3-4]
```
for multiple workers. We will see a message similar to the following displayed:
```
INFO: Setting red003 to 10.1.1.3
INFO: Setting red004 to 10.1.1.4
Added IP's to dnsmasq

# ----------------------------------------------------------------------
# 
#             You have successfuly set static ip(s) for
#             red[003-004] with ips 10.1.1.[3-4]
# 
#             To see changes on server, run:
# 
#             $ cms bridge restart
# 
#             If red[003-004] is connected already, 
#             restart bridge then reboot red[003-004].
# 
#             
# ----------------------------------------------------------------------

```

We then restart the bridge again and reboot workers if necessary.
```
(ENV3) pi@red:$ cms bridge restart
```

---

## Step 5.
To verify that workers have successfuly connected, we call the info command again:
```
(ENV3) pi@red:$ cms bridge info
```
In addition to the information displayed in step 2, we will also have information on the given leases below `# ACTIVE LEASES #` including the lease expiration time, hostnames, MAC addresses, the assigned IP, and the client-ID. Here is an example output.
```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.2 - 10.1.1.122
# Master IP: 10.1.1.1
# 
# # ACTIVE LEASES #
# 2020-04-22 07:08:26 {MAC_ADDRESS} 10.1.1.3 red003 {CLIENT_ID}
# 2020-04-22 07:08:29 {MAC_ADDRESS} 10.1.1.4 red004 {CLIENT_ID}
# ----------------------------------------------------------------------
```

*Note*
The fields in {} will be populated with the worker-specific info.
Additionally, the expiration time is there for reference. There is no need to reassign a static IP after it has already been assigned unless the bridge is re-created.

---

These commands have been designed to prevent several user errors, and will most often have a handled error message for debugging purposes should any issues arise. Additionally, the above commands can be run as many times as needed. There should be no ill effects to doing so.



*IMPORTANT NOTE*
When customizing the IP range of the server or setting static IPs, remember you must abide by RFC 1918 for Private addresses. The IP range must fall within one of the following ip ranges:
```
10.0.0.0        -   10.255.255.255  (10/8 prefix)
172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
192.168.0.0     -   192.168.255.255 (192.168/16 prefix)
```
The default configuration falls within the first of the listed ranges.
