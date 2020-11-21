## A simple command to setup a network bridge between raspberry pi's and a manager pi utilizing dnsmasq
WARNING: This program is designed for Raspberry Pi and must not be executed on your laptop


---
## Table of Contents
* [Quick Start](#quick-start)
* [Usage: Create command](#using-the-create-command)
* [Usage: Restart command](#using-the-restart-command)
* [Usage: Info and Status command](#using-the-info-and-status-commands)
* [Usage: Test command](#using-the-test-command)
* [Usage: Set command](#using-the-set-command)

---
##  Quick Start
---
For reference, we will use the following setup:
* Router Pi has hostname `manager` and is connected to the internet via interface `eth1` (usb -> ethernet) cable
* Router Pi uses interface `eth0` as the private interface to communicate with the workers.
* Cloudmesh is installed using `curl -Ls http://cloudmesh.github.io/get/pi | sh`
* If you choose to use WiFi `wlan0` I do not recommend using ssh to set this up as your ssh pipe may break on step 3 and you will need to wait for the command to complete before you are allowed back in. I recommend using a desktop setup in this case as the command will most likely result in an error. If this is not an option, see the `--background` option in Step 3.
* It is recommended that the manager be connected to the active network hub on the private interface. This will allow the restart process to be even quicker.

* We recommend you have the following network layout for your Pi's. (Note that this program is not specific to kubernetes. It is just a placeholder example)

![Network Layout](https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/master/images/layout.png)

---
**Step 1. Create necessary workers**

Utilize [cmburn](https://github.com/cloudmesh/cloudmesh-pi-burn) to create the workers
```
(ENV3) pi@manager:$ cms burn detect
(ENV3) pi@manager:$ cms burn info
(ENV3) pi@manager:$ cms burn image get latest
(ENV3) pi@manager:$ cms burn create --hostname=red[003-004]
```
Connect them to the private interface (network switch) via ethernet.

We do not need to boot them up yet as if we connect them to the manager now, we will need to reboot them later. (It doesn't hurt though)

*Note* 
Notice how we are not setting the `--ipaddr` option. This is intentional as we want to handle static IPs in a centralized manner now. The program will still work if you configure the Pis with static IPs, but you just won't be able to change them from the manager.

---

**Step 2 Create Bridge.**

Plug the manager Pi into the private interface (network switch) via the built-in ethernet port (eth0)

We can configure our network bridge as follows:
```
(ENV3) pi@manager:$ cms bridge create --interface='eth1'
```

Wait for the program to finish. If no errors, occured, we have successfuly configured the bridge. Check details on the configuration using 
```
(ENV3) pi@manager:$ cms bridge info
```

This will display the following important information (note this is the default setup):
```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.2 - 10.1.1.122
# Manager IP: 10.1.1.1
# 
# # LEASE HISTORY #
# ----------------------------------------------------------------------
```

The `Manager IP` tells us the IP address of the manager on the private interface (eth0).
The `IP Range` tells us the range of suitable IPs we can give to the workers.

In the future, a command will be added to expand the `IP range` dynamically.

---

**Step 3. Restart Bridge**

We can now restart the bridge to reflect these changes:

```
(ENV3) pi@manager:$ cms bridge restart
```

*Note*
If you are ssh'd into the Pi via WiFi, execute `cms bridge restart --background` so that the command is not terminated in the case that the ssh pipeline is broken. The output of the command would be stored in `bridge_restart.log` in the current working directory if this were the case.


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
Restarted bridge service on manager
```
*Note*

This process may take up to 10 attempts. This can be attributed to a slow network, or if the private interface is not connected to an active network hub.

At this point, our bridge is ready and the manager is configured with dhcp services.

We can check to verify the bridge is working by calling
```
(ENV3) pi@manager:$ cms bridge status

# ----------------------------------------------------------------------
# 
# Status of Bridge:
# 
# DHCPCD     -  Service running: True
# DNSMASQ  -  Service running: True
# 
# BRIDGE        - Service running: True
# 
# ----------------------------------------------------------------------

```

---

**Step 4 (optional). Assign static IPs to workers**

We can set a static IP for hostnames as follows:
```
(ENV3) pi@manager:$ cms bridge set red003 10.1.1.3
```
for individual workers and/or
```
(ENV3) pi@manager:$ cms bridge set red[003-004] 10.1.1.[3-4]
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

We then restart the bridge again and boot up (or reboot) the workers.
```
(ENV3) pi@red:$ cms bridge restart --nohup
```
Notice how there is an added option `--nohup`. This option is used when we do not want to reset the entire networking setup of the pi. This is useful in case your are connected to the device via ssh. This will ensure that your pipeline is not broken. Note that we can only use this command after the initial post-creation restart is run once. 

---

**Step 5.**

To verify that workers have successfuly connected, we call the info command again:
```
(ENV3) pi@red:$ cms bridge info
```
In addition to the information displayed in step 2, we will also have information on the given leases below `# ACTIVE LEASES #` including the lease expiration time, hostnames, MAC addresses, the assigned IP, and the client-ID. Here is an example output.
```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.2 - 10.1.1.122
# Manager IP: 10.1.1.1
# 
# # ACTIVE LEASES #
# 2020-04-22 07:08:26 {MAC_ADDRESS} 10.1.1.3 red003 {CLIENT_ID}
# 2020-04-22 07:08:29 {MAC_ADDRESS} 10.1.1.4 red004 {CLIENT_ID}
# ----------------------------------------------------------------------
```
*Note*
The fields under `# ACTIVE LEASES #` only show the devices that have been recognized by the server before the last restart.
It is NOT an indicator of devices currently connected. That feature is still in development.

*Note*
The fields in {} will be populated with the worker-specific info.
Additionally, the expiration time is there for reference. There is no need to reassign a static IP after it has already been assigned unless the bridge is re-created.

---

**Quick Fixes**
Here are some quick actions to try if you are unable to access your workers:
* Restart the bridge
* Restart the workers
* Set a static IP for the hostname
* Utilize the purge option `cms bridge create --interface='eth1' --purge` for a total reconfiguration of the bridge.

---

## Using the create command
```
cms bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE] [--purge]
```
The create command is used for configurating the given raspberry pi as a dhcp server to be used by worker nodes as an internet access point.

| Option        | Description      |
| :-------------: |-------------|
| `--interface`    | The network interface with access to the internet. Usually one of `eth1`, or `wlan0` for most uses. Default `eth1`.|
| `--ip`     | The IP address to give the manager on the private interface. See note below. Default `10.1.1.1`     |
| `--range` | The range of IPs that the server is allowed to give out. Cannot overlap with `--ip`. See note below. Default `10.1.1.2-10.1.1.122` |
| `--purge` | Used in the case that dnsmasq is inexplicably failing after the initial install. Does a complete reinstallation and reconfiguration of dnsmasq. Requires `cms bridge restart` afterwrads for effect. |

**Note**

Per RFC 1918, private addresses should fall in one of the ranges below. Failing to do so will most likely cause issues when trying to connect with the internet. The default falls in the first of these ranges. 

The default configuration will work for most unless the external network overlaps with the `10.1.1.0` network. In which case, one can simply select a suitable subrange from one of the network ranges below. 
```
10.0.0.0        -   10.255.255.255  (10/8 prefix)
172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
192.168.0.0     -   192.168.255.255 (192.168/16 prefix)
```
---

## Using the restart command
```
cms bridge restart [--nohup] [--background]
```
Restarts the bridge and its services. Used when there is a modification to the bridge configuration. Note that the restart command must be called at least once before using the `--nohup` command.
| Option    | Description  |
| :-------: | ----------|
|`--nohup` | Restarts only the `dnsmasq` service and not the `dhcpcd` service (which is the default behavior). This is useful for when simply assigning a static IP to a host or refreshing the lease history. This is particularly of interest for those that are ssh'd into the manager during this process. This option guarantees that the ssh pipe will not be broken after restarting. |
|`--background` | Used for when a user wishes to run the command in the background. Usage for this option is mostly for when users are ssh'd through WiFi and experience broken pipelines. Using `--background` will prevent the command from terminating in the case that a pipeline is broken. The output of the command will be stored in the current working directory on the Pi in a file called `bridge_restart.log` |

---

## Using the info and status commands
```
cms bridge status
```
Use the status command to check on the status of the bridge itself. If all services are running, then the bridge is active. 

```
cms bridge info
```
The info command displays information about the current configuration of the bridge. Information includes details like the IP address of the manager, the IP range, and the lease history of the bridge. The following is a sample output with the default configuration.

```
# ----------------------------------------------------------------------
# 
# IP range: 10.1.1.2 - 10.1.1.122
# Manager IP: 10.1.1.1
# 
# # LEASE HISTORY #
# 2020-04-28 14:21:40 b8:27:eb:57:f6:65 10.1.1.9 red002 01:b8:27:eb:57:f6:65
# 2020-04-28 14:21:40 b8:27:eb:c9:b1:ff 10.1.1.42 red003 01:b8:27:eb:c9:b1:ff
# ----------------------------------------------------------------------
```

The first two entries of each row show the date and time in which the lease expires and is set to renew. The next entries show, in order, the MAC address, the assigned IP address, the hostname, and the client id.

**Note**
The lease history is not a list of connected devices. It simply demonstrates the known information about each lease it has given out during its lifetime. To check if a host is connected, see the `test` command usage below

---

## Using the test command
```
cms bridge test HOSTS
```
The test command is used to verify a connection with the given hostnames. Using a ping attempt, the command will first verify that the
server has seen the specified host before, and then check to see if there are transmitted packets.

Example usage:
```
cms bridge test red002

cms bridge test red002,red005

cms bridge test red[002-004]
```

---

## Using the set command

```
cms bridge set HOSTS ADDRESSES
```
Used to assign static IPs to given hosts. The given addresses must fall in the current ip range of the server. The range can be viewed using `cms bridge info`. After setting the IPs, the bridge must be restarted. 
```
cms bridge restart --nohup
```

Example usage:
```
cms bridge set red002 10.1.1.2

cms bridge set red[003-005] 10.1.1.[3-5]

```

---

**Other recommendations**
* I find that this system works even better if this bridge is configured on a pi that is completely separate from any other pi in a cluster. That way, you can configure a single pi for general use similar to an internet modem and then develop several pi clusters through the use of it.

**Dependencies**
* [dnsmasq](https://wiki.archlinux.org/index.php/dnsmasq) - Installed upon first call to `create` and reinstalled when using `--purge`
* [dhcpcd](https://wiki.archlinux.org/index.php/Dhcpcd) - Pre-installed with raspbian OS
