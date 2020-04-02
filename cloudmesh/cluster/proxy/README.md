# PROXY Notes

Quetsion: why add xyz

    xyz ...

* unbound - dns server - on pi
* squid - on pi

# Attempting to follow suggestions provided

## Step 1. Configure interfaces file on "master"
```
**Per Guide:**


Here is an outline of what you would need on your "master" pi:
For the two network interfaces I will assume eth0 is the "private"
network and "eth1" is the "external" interface. Your
/etc/network/interfaces file should look something like this:

   # The loopback interface
   auto lo
   iface lo inet loopback
   # Private interface
   auto eth0
   iface eth0 inet static
   address 192.168.1.254
   netmask 255.255.255.0
   # External interface
   auto eth1
   iface eth1 inet dhcp

Note, eth0 could also be a "10." or "172.16." address, it doesn't matter
as long as it is a "private" network, but the rest of the following
assumes the above configuration.
```

For the purposes of keeping track of my steps, it is worth noting the network configuration for eth0 in my setup. 

Using one NETGEAR unregulated switch with a network address of `169.254.x.x` and subnet mask `255.255.0.0`

As such, my `/etc/network/interfaces` file looks as follows:
```
# The loopback interface
auto lo
iface lo inet loopback

# Private interface
auto eth0
iface eth0 inet static
address 169.254.10.254
netmask 255.255.0.0

# External Interface
auto eth1
iface eth1 inet dhcp
```

Additionally, the worker Pi (hostname red001) that we are trying to provide with internet access has a static IP of `169.254.10.10`

The interfaces file for red001 is as follows:
```
auto eth0
iface eth0 inet static
   address 169.254.10.10/1
```

At this point, the master has access to red001 via the private interface through eth0.

## Step 2. Installation and configuration of unbound
```
**From Guide:**

Also note that to get a dhcp address from IU the device must be
registered. I can do this if you send me the MAC address.
You will need a DNS server, I like "unbound" which should be available
as a package, so "apt-get install unbound" on your master pi.
The unbound.conf file should look something like:

   server:
       interface: 192.168.1.254
       interface: 127.0.0.1
       access-control: 192.168.1.0/24 allow
       do-not-query-localhost: no
       hide-identity: yes
       hide-version: yes
   forward-zone:
       name: "."
       forward-addr: 129.79.1.1   # IU Primary
       forward-addr: 129.79.5.100 # IU Secondary
```

I have attempted to replace certain options for use on my network setup, but I am unsure if I got certain things correct.
```
/etc/unbound/unbound.conf:

server:
	interface: 169.254.10.254
	interface: 127.0.0.1
	access-control: 169.254.1.0/16 allow
	do-not-query-localhost: no
	hide-identity: yes
	hide-version: yes

forward-zone:
	name:"."
	forward-addr: 8.8.8.8
	forward-addr: 8.8.4.4   

```
I have changed certain options in the `server` configuration to match up with the setup discussed above.

**Question 1**
In the `forward-zone` part, I have replaced the IU primary and secondary DNS server IP addresses with Google's primary and secondary (as this is a home setup away from campus). I am wondering if this is the correct specification for `forward-addr`. Specifically, I am wondering if there is an even more accurate address to provide for this option.

# # Step 3. Configuring dhcpd server

This is the main area where I begin to run into issues.

```
**From Guide:**
You will need to configure your dhcpd server (dhcpd.conf), something
like:

   subnet 192.168.1.0 netmask 255.255.255.0 {
       option routers 192.168.1.254;
       option domain-name-servers 192.168.1.254;
       range 192.168.1.1 192.168.1.127;
   }
```

Here the issue is the `dhcpd.conf` file does not exist. I am looking for this file in `/etc/dhcp/` as this is the logical location for it, but there is no default file. (Although there is a `dhclient.conf` if that is of any relevance.)

Upon researching this issue, I found [this](https://www.raspberrypi.org/forums/viewtopic.php?t=66514) article which is essentially the issue (missing file). In this article, it states that the functionality of `dhcpd.conf` has been moved to `/etc/dhcpcd.conf` which intuitively makes sense. My research into networking Raspberry Pi's has revealed that a lot of networking settings (including those setup in `/etc/network/interfaces`) can be taken care of in this new file. However, I have been unsuccesful in using this file to take care of Step 1.

Unfortunately, this is an issue I have been unable to get past. The service that runs using the `dhcpcd.conf` file is the `dhcpcd` service. This service is unable to start due to conflicts presented by the `networking` service, which is affected by changes to `/etc/network/interfaces`

Upon running the command
```
$ systemctl status dhcpcd.service
```
the following log is returned
```dhcpcd.service - dhcpcd on all interfaces
   Loaded: loaded (/lib/systemd/system/dhcpcd.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Thu 2020-04-02 17:11:46 EDT; 2min 50s ago
  Process: 4919 ExecStart=/usr/lib/dhcpcd5/dhcpcd -q -b (code=exited, status=6)

Apr 02 17:11:46 red systemd[1]: Starting dhcpcd on all interfaces...
Apr 02 17:11:46 red dhcpcd[4919]: Not running dhcpcd because /etc/network/interfaces
Apr 02 17:11:46 red dhcpcd[4919]: defines some interfaces that will use a
Apr 02 17:11:46 red dhcpcd[4919]: DHCP client or static address
Apr 02 17:11:46 red systemd[1]: dhcpcd.service: Control process exited, code=exited, status=6/NOTCONFIGUR
Apr 02 17:11:46 red systemd[1]: dhcpcd.service: Failed with result 'exit-code'.
Apr 02 17:11:46 red systemd[1]: Failed to start dhcpcd on all interfaces.
```

What this tells me is that defining the interfaces in `/etc/network/interfaces` causes conflicts that disables `dhcpcd`

It seems that we should move the interface settings from `/etc/network/interfaces` to `/etc/dhcpcd.conf` to resolve this conflict. I believe we can do this as there are several tutorials for setting static ip addresses through this file. Notably, [this](https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address) answer on stack exchange details possible ways of doing this. Unfortunately, I have not been successful in doing this.

I'm wondering if [this](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md) might be of any use.


## Step 4. NAT routing

I have been able to get through these steps, however I cannot test it as I cannot get past step 3.

```
You will then need to configure "NAT" for routing the internal traffic
to external. I have not done this with debian but there are many
examples on line.
First you need to enable IP forwarding, adding this line to

/etc/sysctl.conf and rebooting:
   net.ipv4.ip_forward = 1

Then configure iptables (use sudo to run these commands; not tested, but

I think this is right):

   iptables --table nat -A POSTROUTING -o eth1 -j MASQUERADE
   iptables -A FORWARD -i eth1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
   iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT

You'll need to look up how to automatically apply those iptables
commands after a reboot. I think for debian it needs the
"iptables-persistent" package or maybe put them in /etc/rc.local if that
is supported.
Then be sure that eth0 is connected to your hub and eth1 is connected to
IU network.
Hope this helps....
I forgot to add, all of the other pis in the cluster should have this in
their /etc/network/interfaces, (assuming that eth0 is the on-board
interface):

   auto eth0
   iface eth0 inet dhcp
```