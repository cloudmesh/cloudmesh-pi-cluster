
# Here I am documenting a fresh run including configuring burning master and utilizing cm-pi-burn 

# Step 1. Burn pi 4 master
This is trivial. Plenty of guides exist in the cloudmesh repo and the internet

# Step 2. Burn worker(s) with cm-pi-burn
Again, trivial.

# Step 3. Configure iptables on master
Enable IPv4 forwarding
Edit /etc/sysctl.conf and uncomment this line:
```
net.ipv4.ip_forward=1
```
`/proc/sys/net/ipv4/ip_forward` should be 1 upon reboot

**Assumption:**
eth0 is private interface (network switch to workers)
eth1 is external interface (internet connection)

With the above assumption, we execute the following commands:
```
$ sudo iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
$ sudo iptables -A FORWARD -i eth1 -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT
$ sudo iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
```

Save rules in case of reboot.
```
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

Edit `/etc/rc.local` and add this just above "exit 0" to install these rules on boot.
```
iptables-restore < /etc/iptables.ipv4.nat
```

The master is now ready to direct traffic from eth0 to eth1

# Step 4. Configure network interface on worker
If `cm-pi-burn` was used for the workers, then `/etc/network/interfaces` should have a configuration similar to the following:
```
auto eth0
iface eth0 inet static
   address 169.254.10.10/16
```
Note that for this example, we are assuming the worker has a static IP of 169.254.10.10 on the eth0 interface.

To configure the worker to use the master as a "proxy" to the internet, we add two more lines to the interfaces file. `/etc/network/interfaces` should look like:
```
auto eth0
iface eth0 inet static
   address 169.254.10.10/16
   gateway 169.254.10.1
   dns-nameservers 8.8.8.8 8.8.4.4
```
We added two options:
* `gateway`
* `dns-nameservers`
The `gateway` option should be the IP address of the master on eth0. `dns-nameservers` is the field for nameservers to utilize. In this example, we just use google's primary and secondary DNS.

# Step 5. Test connection
If the above steps have been executed properly, then we should be able to ping for data from any website. We can do some tests...

We can ping `google.com`
```
ping google.com
PING google.com (...): 56 data bytes
64 bytes from ...: icmp_seq=0 ttl=53 time=35.910 ms
64 bytes from ...: icmp_seq=1 ttl=53 time=22.224 ms
64 bytes from ...: icmp_seq=2 ttl=53 time=20.391 ms
64 bytes from ...: icmp_seq=3 ttl=53 time=23.632 ms
^C
--- google.com ping statistics ---
4 packets transmitted, 4 packets received, 0.0% packet loss
```
or any other website to verify connection. 





