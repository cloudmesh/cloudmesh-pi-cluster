# Cloudmesh NFS

## Prerequisites/Notes

Worker pis must connect wait for network connection on reboot. Enable this by entering ```worker$ sudo raspi-config``` , selecting ```System Options``` , scrolling to and selecting ```Network at Boot``` , and enabling waiting for network connection on boot.

The root user on the worker pi will have the authority to access files on the manager pi as root. Please consider the security implications before proceeding

## Install

This command will install the necessary package to perform network file sharing onto your manager pi:

```
pi@red$ cms pi nfs install
```
## Share Directory

Share a directory on your manager pi to your worker pis using the following command:

```
pi@red$ cms pi nfs share --paths=PATHS --hostnames=HOSTNAMES
```

Example:

```
pi@red$ cms pi nfs share --paths="/home/pi/Stuff,/mnt/nfs" --hostnames="red,red01,red02"
```

The ```--paths``` argument takes first the path to the master directory you wish to share and second the path to the shared directory. The command will create the shared directory on your manager and worker pis. We recommend naming this directory ```/mnt/nfs``` 

The ```--hostnames``` command takes first the manager hostname and next the hostnames of the workers you wish to share to.

## Unshare Directory

```
pi@red$ cms pi nfs unshare --path=PATH --hostnames=HOSTNAMES
```

Example, unsharing to a specific worker:

```
pi@red$ cms pi nfs unshare --path="/mnt/nfs" --hostnames="red01"
```

Example, unsharing to all workers (taking down NFS share from manager):

```
pi@red$ cms pi nfs unshare --path="/mnt/nfs" --hostnames="red,red01,red02"
```

The ```--path``` argument takes the path to the shared directory. The ```hostnames``` argument takes the names of the pis to unshare the manager's directory to. If the names of only worker pis are included, then those specific worker pis will lose access to the shared directory. If the manager is included along with all worker pis, then the entire NFS sharing functionality will be taken down. 
