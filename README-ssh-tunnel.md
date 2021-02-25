## Port Forwarding Tutorial

### How to do a local port forward for internal node SSH access via the manager node

In this image below we setup a ssh tunnel on the manager pi to enable ssh access from the laptop to the worker node Red001. 

The manager and laptop must both be included in red001's `~/.ssh/authorized_hosts` file.

![](https://github.com/cloudmesh/cloudmesh-pi-cluster/raw/main/images/ssh-port-forward.PNG)

We create one tunnel for each worker each with a unique wlan_ip:port assigned.

Now in the laptop `~/.ssh/config` file we add:

```
Host red
     HostName    red.local
     User        pi

Host red001
     HostName    red.local
     User        pi
     Port       8001

Host red002
     HostName    red.local
     User        pi
     Port        8002
```

Finally we can ssy from the laptop to the worker.

```
you@laptop:~ $ ssh red001
```

**However, this tunnel is not permanent as is.** Besides manager or worker restarts, it is also subject to communication failures, such as timeouts, that will cause the tunnel to break. This will force the user to re-run the command to create the tunnel, and in some cases, find and kill a failed but still existing tunnel process. 

For additional visualizations and discussion of local and remote port forwarding see <http://dirk-loss.de/ssh-port-forwarding.htm>

### How to make a local port forward tunnel persistent using Autossh and Systemd

Autossh is a program designed to automatically restart SSH sessions and tunnels.

Systemd is a Linux system and service manager used by Raspi OS.

We use systemd to install an autossh service that starts on system boot to establish the ssh tunnel.

Create the below file. Notice this requires the wifi IP address on the manager (wlan0 e.g. 192.168.1.24).

`/etc/systemd/system/autossh-red001.service`

```
[Unit]
Description=AutoSSH tunnel service to red001 on local port 8001
After=multi-user.target

[Service]
User=pi
Group=pi
Environment="AUTOSSH_GATETIME=0"
ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -i /home/pi/.ssh/id_rsa -NL 192.168.1.24:8001:localhost:22 pi@red001

[Install]
WantedBy=multi-user.target
```

To get the service to start and be enabled on system restart we need to run the following commands.

```
sudo systemctl daemon-reload
sudo systemctl start autossh-red001.service
sudo systemctl enable autossh-red001.service
```

> NOTE: As we are binding the tunnel to a dynamically assigned address on our wlan0 interface. The tunnel will not function if wlan0 interface is assigned a different IP.

Currently the command below will setup a autossh tunnel for ssh access to the workers.

```
pi@manger $ cms host tunnel create red00[1-2] [--port]
```


### How to use ProxyJump for SSH access to internal node via the manager node

It turns out setting up a port forward for simple ssh access to the workers via the manger is over complicated.

ProxyJump is an SSH option that exists to simply this purpose. It is also more reliabe as the tunnel is setup on demand.

See the example below.

```
ssh -J pi@red.local pi@red001
```

We can also do this with a only `~/.ssh/config` file.

```
Host red
   Hostname red.local
   User	    pi
   
Host red001
   Hostname red001
   User	    pi
   ProxyJump red
```

No we can simply setup a tunnel on demand as we access the worker.


```
you@laptop:~ $ ssh red001
```

### Can ProxyJump be used for arbitary services?

I don't know yet. Based on a quick glance at this article, the answer is **no**, but it can be useful if you need to tunnel through multiple hosts before starting a remote port forward.

<https://medium.com/maverislabs/proxyjump-the-ssh-option-you-probably-never-heard-of-2d7e41d43464>

### Use local port forward to expose arbitrary service

So, port forwarding is still useful to expose arbitrary services.

In the example below we expose a worker running cloudmesh-openapi on port 80 to the laptop with a local port foward. Again we can make this permanent with autossh and systemd.

![](https://github.com/cloudmesh/cloudmesh-pi-cluster/raw/main/images/web-port-forward.PNG)

### Reccmmendatoins

For simple ssh access we make a command (or Gregor might have already done this, I haven't reviewed his work yet)

```
cms ssh config NAMES MANAGER [--laptop]
```

e.g.

```
 cms ssh config red00[1-2] red --laptop=anthony@anthony-ubuntu.local
```
We will probably turn `cms host tunnel create` into a command to expose an arbirary cluster-internal service to the laptop (not just ssh). For example accessing a web page running on a worker.

```
cms host tunnel create NAMES SERVICE_PORTS EXTERNAL_START_PORT
```

e.g. 

```
cms host tunnel create red00[1-2] 80 8080
```

Now from laptop we can browse to http://red.local:8080 and http://red.local:8081 to access the web pages on red001:80 and red002:80 respectively. (edited) 
