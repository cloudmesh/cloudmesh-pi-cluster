# Documentation

This README is managed in 

* [README.md](https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/master/README.md)
* <https://github.com/cloudmesh/cloudmesh-pi-cluster>


## About

This document describes how to set up a variety of cluster platforms on
a number of raspberry PI's. We used Pi3B+ and Pi4 with 32 GB SD cards.
You will idially wnat to have a minimum of 3 Pi's.


## Instalation

### Creating the SD Cards

We have chosen not to use network booting, but boot from teh SD Crads.
For this we will use our special `burn` program to burn the Pi's. This
allows you to immediately start with an OS that has all the needed
information on it. However we need one master py that we simply
configure with the pi imager.

TODO: point to the documentation

TODO: Briefly describe how we burn the master and set it up

TODO: Then describe briefly how we burn


### Prerequisite

Once you have set up the master and have network access, you must
conduct the following steps

First we update the system and install python3 in ~/ENV3 with the
command, activate it, and generate an ssh key

```bash
curl -Ls http://cloudmesh.github.io/get/pi | sh
source ~/ENV3/bin/activate
ssh-keygen
```

These steps have  only to be done once on your master Pi.


### User install

The instalation for cloudmesh on the Pi cluster package is simple:

```bash
pip install cloudmesh-pi-cluster
```

### Developer install

In case you like to contribute to the code, we provide a conveniennt
mechanism for you to download all source code repositories from Git. YOu
will find in the directory wheere you downloaded the code all source
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

To get a list of commands related to the cloudmesh cluster simply use

```
cms help
```

To just list the cluster command manual page use

```
cms help pi
```

to just show the usage use

```
cms pi
```


## Setting LEDS

``` bash
$ cms pi led green on
$ cms pi led green off
$ cms pi led red on
$ cms pi led red off
```

## Getting the Temperature

Please note that the times are not exact as there is a slight delay
between getting the data and getting the data form the Pi.

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

## Watching the temperature continiously

To watch the temperature continiously in the termoinal, use a repeat rate.  
To end the  program press CTRL-C

```bash
cms pi temp "red,red[01-03]" --rate=1.0
```

## Graph

### Sparkline

```bash
cms pi temp "red,red[01-03]"  --output=sparkline
▄▆█▃
```

### Bar

```bash
cms pi temp "red,red[01-03]"  --output=bar
```

![Display as bars](images/bar.png)

### Line

```bash
cms pi temp "red,red[01-03]"  --output=line
```

![Display as bars](images/line.png)


### Browser

```bash
cms pi temp "red,red[01-03]"  --output=browser
```

![Display as bars](images/browser.png)

### Live animation

A live animation is available with

```bash
cms pi temp "red,red[01-03]" --rate=1 --output=live
```

![Display as bars](images/live.png)

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

## Load Average

```

cms pi load "red,red[01-03]" --rate=1 --output=graph
```

```
cms pi load "red,red[01-03]" --rate=1 --output=graph

+-------+-------+-------+------+--------------+------------+
| host  | 1     | 5     | 10   | proc.running | proc.total |
+-------+-------+-------+------+--------------+------------+
| red   | 10.01 | 10.04 | 9.58 | 1            | 142        |
| red01 | 0.01  | 0.02  | 0.0  | 1            | 125        |
| red02 | 0.03  | 0.04  | 0.01 | 1            | 128        |
| red03 | 0.09  | 0.08  | 0.02 | 1            | 125        |
+-------+-------+-------+------+--------------+------------+
```
NOTES

 mpstat -P ALL
 nmon

## Stress test

* <https://manpages.ubuntu.com/manpages/artful/man1/stress-ng.1.html#examples>


```
sudo apt-get install -y stress-ng
```

Memory test

```
stress-ng --vm 8 --vm-bytes 80% -t 1h
```

