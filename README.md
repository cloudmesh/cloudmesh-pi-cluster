# Documentation

This README is managed in 

* [README.md](https://github.com/cloudmesh/
  cloudmesh-pi-cluster/blob/master/README.md)
* <https://github.com/cloudmesh/cloudmesh-pi-cluster>

## About

This document describes how to set up a variety of cluster platforms on
a number of Raspberry Pi's. We used Pi3B+ and Pi4 with 32 GB SD cards.
You will ideally want to have a minimum of 3 Pi's.

In addition to this document, we have additional we have separate
documents that showcase how to convert your cluster into a

* [Spark Cluster (under development)](https://github.com/cloudmesh/
  cloudmesh-pi-cluster/blob/master/cloudmesh/pi/cluster/spark/README.md)
* [Hadoop Cluster (under development)](https://github.com/cloudmesh/
  cloudmesh-pi-cluster/blob/master/cloudmesh/pi/cluster/hadoop/README.md)
* [Kubernetes Cluster (under development)](https://github.com/
  cloudmesh/cloudmesh-pi-cluster/blob/master/cloudmesh/pi/cluster/k3/README.md)
* [MongoDB Cluster (under development)](https://github.com/cloudmesh/
  cloudmesh-pi-cluster/blob/master/cloudmesh/pi/cluster/mongo/README.md)

## Installation

### Creating the SD Cards

We have chosen not to use network booting, but boot from the SD Cards.
For this, we use our unique `burn` program to burn the Pi's. This
allows you to immediately start with an OS that has all the needed
information on it. However, we need one master Pi that we
configure with the Pi imager.  

The detailed procedure on how to proceed with the burning procedure can be seen
[here](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/master/README.md)  

#### Setting up the Master Pi

* Use the Raspberry Pi Imager to burn an SD card by following the recommended 
  instructions on the official [website](https://www.raspberrypi.org/blog/
  raspberry-pi-imager-imaging-utility/). Also make sure that you install the 
  latest stable release of the Raspbian OS you are using. We are using the 
  32-bit Raspbian Buster, May 2020 build. 
* Once burned, insert the SD card in the Master Pi and then follow the 
  on-screen instructions to configure the OS. Make sure you connect to Wi-Fi, 
  change the default hostname, and enable SSH by using the pre-installed 
  Raspberry Pi Configuration tool.
* The next segment of code creates a venv named ~/ENV3, creates a ssh-key, adds 
  it to the ssh-agent, and then downloads the latest Raspbian(Lite) image. 
  While adding the ssh-key, be sure to choose a strong passphrase.  

  ```bash
  pi@red:$ ssh-keygen
  pi@red:$ curl -Ls http://cloudmesh.github.io/get/pi | sh
  pi@red:$ source ~/ENV3/bin/activate

  (ENV3) pi@red:$ source ~/.bashrc
  (ENV3) pi@red:$ cms burn image get latest
  (ENV3) pi@red:$ cms burn image ls
  ```

#### Setting up Worker Pis

1. Plug in a SD Card Writer to the Master Pi and see if it is detected using 
   the commands shown below. Follow the on-screen propmts and instructions  

   ```bash
   (ENV3) pi@red:$ cms burn detect
   (ENV3) pi@red:$ cms burn info
   ```

2. Set your default SD Card device as shown below. Replace ```/dev/sdx``` with 
   the drive name reported by the ```info``` command  

   ```bash
   (ENV3) pi@red:$ export DEV=/dev/sdx
   ```

3. Start burning the SD Cards. If you do not have a multi-card writer, you 
   will have to plug out your device and replace the SD Card with the next one 
   once the previous one has finished burning. Follow the onscreen instructions.

   ```bash
   (ENV3) pi@red:$ cms burn create --hostname=red[001-002]
   ```

### Prerequisite

Once you have set up the master and have network access, you must
conduct the following steps

First, we update the system and install python3 in ~/ENV3 with the
command, activate it and generate an ssh key

```bash
curl -Ls http://cloudmesh.github.io/get/pi | sh
source ~/ENV3/bin/activate
ssh-keygen
```

These steps have only to be done once on your Master Pi.

### User install

The installation for cloudmesh on the Pi cluster package is simple:

```bash
pip install cloudmesh-pi-cluster
```

### Developer install

In case you like to contribute to the code, we provide a convenient
mechanism for you to download all source code repositories from Git. You
find in the directory where you downloaded the code all source
code. The reason we recommend that you do this in a directory cm is that
it is the same for all developers and that all the source code is
located in one directory.

```bash
mkdir ~/cm
cd cm
cloudmesh-installer get pi
```

## Using the Cluster commands

### Getting Help

To get a list of commands related to the cloudmesh cluster use

```
cms help
```

To list the cluster command manual page use

```
cms help pi
```

to show the usage use

```
cms pi
```

### Setting LEDS

In case you want to signal which Pi is which we can leverage the on
board LEDs. You have a green and red LED that you can control as follows:

``` bash
$ cms pi led green on
$ cms pi led green off
$ cms pi led red on
$ cms pi led red off
```

### Getting the Temperature

Sometimes it is useful to view the temperature of the PI's as it could
have performance issues due to overheating, and the PIs are forced to
throttle. Hence it is a good idea to vent your Pis very well

Please note that the times are not exact as there is a slight delay
between getting the data and getting the data from the Pi.

```bash
cms pi temp "red,red[01-03]"
+-------+--------+------+----------------------------+
| host  | cpu    | gpu  | date                       |
+-------+--------+------+----------------------------+
| red   | 56.965 | 56.0 | 2020-03-28 14:34:46.926618 |
| red01 | 62.322 | 62.0 | 2020-03-28 14:34:46.949065 |
| red02 | 65.731 | 65.0 | 2020-03-28 14:34:46.933548 |
| red03 | 55.017 | 54.0 | 2020-03-28 14:34:47.218047 |
+-------+--------+------+----------------------------+
```

#### Watching the temperature continuously

To watch the temperature continuously in the terminal, use a repeat rate.  
To end the  program press `CTRL-C`

```bash
cms pi temp "red,red[01-03]" --rate=1.0
```

#### Sparkline

You can also get the temperature as sparkline with

```bash
cms pi temp "red,red[01-03]"  --output=sparkline
▄▆█▃
```

#### Bar

A Bar graph is created with

```bash
cms pi temp "red,red[01-03]"  --output=bar
```

<!--
![Display as bars](images/bar.png){: width="400"}
-->

<img src="images/bar.png" alt="Display as bars" title="Display as bars" width="400"/>

#### Line

A line graph is created with

```bash
cms pi temp "red,red[01-03]"  --output=line
```

<!--
![Display as bars](images/line.png)
-->

<img src="images/line.png" alt="Display as line" title="Display as line" width="400"/>

#### Browser

The output can also be looked at in a browser

```bash
cms pi temp "red,red[01-03]"  --output=browser
```

<!--
![Display as bars](images/browser.png)
-->

<img src="images/browser.png" alt="Display in browser" title="Display in browser" width="400"/>

#### Live animation

A live animation is available with

```bash
cms pi temp "red,red[01-03]" --rate=1 --output=live
```

<!--
![Display lie](images/live.png)
-->

<img src="images/live.png" alt="Display live" title="Display live" width="400"/>

## Memory

```bash
cms pi free "red,red[01-03]" --rate=1
```

```
+-------+-----------+----------+----------+------------+-----------+-----------+------------+-----------+-----------+
| host  | mem.total | mem.used | mem.free | mem.shared | mem.cache | mem.avail | swap.total | swap.used | swap.free |
+-------+-----------+----------+----------+------------+-----------+-----------+------------+-----------+-----------+
| red   | 4.1 GB    | 109.5 MB | 3.8 GB   | 42.4 MB    | 188.2 MB  | 3.8 GB    | 104.9 MB   | 0 Bytes   | 104.9 MB  |
| red01 | 4.1 GB    | 99.8 MB  | 3.8 GB   | 34.0 MB    | 177.1 MB  | 3.8 GB    | 104.9 MB   | 0 Bytes   | 104.9 MB  |
| red02 | 4.1 GB    | 108.8 MB | 3.8 GB   | 34.0 MB    | 176.1 MB  | 3.8 GB    | 104.9 MB   | 0 Bytes   | 104.9 MB  |
| red03 | 4.1 GB    | 100.5 MB | 3.8 GB   | 34.0 MB    | 176.4 MB  | 3.8 GB    | 104.9 MB   | 0 Bytes   | 104.9 MB  |
+-------+-----------+----------+----------+------------+-----------+-----------+------------+-----------+-----------+
```

This can also be invoked repeatedly with

```
cms pi free "red,red[01-03]" --rate=1.0
```

### Getting the Load Average

The load average can be obtained with

```

cms pi load "red,red[01-03]" --rate=1

+-------+-------+-------+------+--------------+------------+
| host  | 1     | 5     | 10   | proc.running | proc.total |
+-------+-------+-------+------+--------------+------------+
| red   | 10.01 | 10.04 | 9.58 | 1            | 142        |
| red01 | 0.01  | 0.02  | 0.0  | 1            | 125        |
| red02 | 0.03  | 0.04  | 0.01 | 1            | 128        |
| red03 | 0.09  | 0.08  | 0.02 | 1            | 125        |
+-------+-------+-------+------+--------------+------------+
```

We have the same formats available just as in the temperature monitor.
Most useful is the live data which you can obtain with

```bash
cms pi load "red,red[01-03]" --rate=1 --output=graph
```

### Stress test

To put some load on the system, you can use the command stress-ng

* <https://manpages.ubuntu.com/manpages/artful/man1/stress-ng.1.html#examples>

It can be installed on a PI with

```
sudo apt-get install -y stress-ng
```

A  memory test can be started with

```
stress-ng --vm 8 --vm-bytes 80% -t 1h
```

When watching with

```
cms pi load "red,red[01-03]" --rate=1 --output=graph
```

You will see the graph reacting to it.

## Other Monitoring programs

Other Monitoring programs include

```
mpstat -P ALL
nmon
```

Please make sure you install them first before using them.

