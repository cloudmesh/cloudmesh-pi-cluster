# PROXY Notes

Quetsion: why add xyz

    xyz ...

Trying to follow this tutorial on configuring a subnet hosted by the
master pi.

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

I assume you will use /etc/hosts for your local names, but you could
also set up a local zone in unbound if you prefer. I do not show this
now however.

** Issue Here. /etc/dhcp/dhcpd.conf does not exist **
You will need to configure your dhcpd server (dhcpd.conf), something
like:

   subnet 192.168.1.0 netmask 255.255.255.0 {
       option routers 192.168.1.254;
       option domain-name-servers 192.168.1.254;
       range 192.168.1.1 192.168.1.127;
   }

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
