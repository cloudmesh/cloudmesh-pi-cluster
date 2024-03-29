---
date: 2021-04-30
title: "Introduction to NFS"
linkTitle: "Introduction to NFS"
description: "This post will cover setting up NFS on a RaspberryOS Cluster"
draft: True
author: Gregor von Laszewski ([laszewski@gmail.com](mailto:laszewski@gmail.com)) [laszewski.github.io](https://laszewski.github.io)
resources:
- src: "**.{png,jpg}"
  title: "Image #:counter"
---

{{< imgproc image Fill "600x300" >}}
TODO: Caption for the image
{{< /imgproc >}}

{{% pageinfo %}}

This tutorial walks through how to share a volume between a manager pi and its workers in a RaspberryOS cluster. A tutorial on creating a RaspberryOS cluster can be found here:

<https://cloudmesh.github.io/pi/tutorial/raspberry-burn/>

**Learning Objectives**

* Learn how to use ```cms pi nfs``` to create an NFS share for a RaspberryOS cluster
  
**Topics covered**

{{% table_of_contents %}}

{{% /pageinfo %}}

## Introduction

NFS Protocol allows remote access to files across networks. Users on client machines can access filesystems on servers in the same way they would if the filesystem was on local storage. 

## Install

This command will install the necessary package to perform network file sharing onto your manager pi:

```
pi@red$ cms pi nfs install
```

Example if the Pi has a username that is not "pi":

```
pi@red$ cms pi nfs install --username=myusername
```

## Share Directory

Share a directory on your manager pi to your worker pis using the following command:

```
pi@red$ cms pi nfs share --paths=PATHS --hostnames=HOSTNAMES
```

Example:

```
pi@red$ cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red0[1-3]"
```

The ```--paths``` argument takes first the path to the master directory you wish to share and second the path to the shared directory. The command will create the shared directory on your manager and worker pis. We recommend naming this directory ```/mnt/nfs``` 

The ```--hostnames``` command takes first the manager hostname and next the hostnames of the workers you wish to share to.

Example if the Pi has a username that is not "pi":

```
pi@red$ cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red0[1-3]" --username=myusername
```

The user can also choose to share a USB:

Example:

```
pi@red$ cms pi nfs share --paths="/mnt/nfs" --hostnames="red,red0[1-3]" --usb=yes
```

The usb parameter creates an interactive installation that prompts the user to choose from a list of devices connected to the manager Pi.
Then the chosen device serves as the nfs for the hostnames.

## Unshare Directory

The shared folders will persist after rebooting the cluster even if the user deletes them. The way to delete the folders for good
is to use the unshare command, which also halts sharing/broadcasting the nfs to the workers. The command's structure is the following:

```
pi@red$ cms pi nfs unshare --path=PATH --hostnames=HOSTNAMES
```

Example, unsharing to a specific worker:

```
pi@red$ cms pi nfs unshare --path="/mnt/nfs" --hostnames="red01"
```

Example, unsharing to all workers (taking down NFS share from manager):

```
pi@red$ cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red0[1-3]"
```

Example if the Pi has a username that is not "pi":

```
pi@red$ cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red0[1-3]" --username=myusername
```

The ```--path``` argument takes the path to the shared directory. The ```hostnames``` argument takes the names of the pis to unshare the manager's directory to. If the names of only worker pis are included, then those specific worker pis will lose access to the shared directory. If the manager is included along with all worker pis, then the entire NFS sharing functionality will be taken down. 
