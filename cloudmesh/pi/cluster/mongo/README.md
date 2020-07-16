# Setting up a Pi MongoDB Cluster 

**NOTE**: We are using the 32-bit Raspbian
Buster operating system for our Pi cluster. Unfortunately, MongoDB only supports
the legacy 2.4.14 version for a 32-bit operating system. Hence the MongoDB
version deployed will be an older version which is no longer supported. Also,
32-bit builds of MongoDB are limited to less than 2GB of data. 

## Prerequisites

The master and workers must be set up as described in the general setup section.
The worker Pis have to be connected to the internet via the master using the
```cms bridge``` command. The documentation for the command can be found here:

<https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/bridge>

## Installation

This following command will install MongoDB to the master and workers provided.

```bash 
cms pi mongo install [--master=MASTER] [--workers=WORKERS] 
```

## Other Available Commands

Uninstall MongoDB on the master and/or any worker. This will also remove all of
the installed dependancies.

```bash
cms pi mongo uninstall [--master=MASTER] [--workers=WORKERS] 
```

Start the mongod client. The mongod client can start in one of two
implementations depending on the ```--type``` argument provided. If the
```--type``` argument is not specified then the ```local``` option will be
considered by default.  

```bash  
cms pi mongo start [--type=TYPE] [--master=MASTER] \
[--workers=WORKERS] [--port=PORT] [--dbpath=DBPATH] [--ip_bind=IP_BIND] 
```

1. ```--type=local```  

	The mongod client will be launched on the master Pi only. The ```--port``` 
	```--dbpath``` and ```--ip_bind``` arguments may be provided if you want to
	specify the port and the database path respectively. If not provided, the
	values will default to ```--port=27011```, ```--dbpath=/home/pi/data/db``` and
	```--ip_bind=127.0.0.1```  

	Example usage:

	```bash 
	cms pi mongo start --type=local --master=blue --ip_bind=10.1.1.100 --port=27017 \
	--dbpath=/home/pi/data/db
	```
	

2. ```--type=replica```  

	The mongod client will be launched in a Replication Set configuration.
	Currently, this command only supports launching a replica set in an odd
	configuration only with 3 Workers acting as secondary and 1 Master as primary.
	You are required to provide the ```--master``` , ```--workers``` and
	```--port``` arguments   which specify which workers will be deployed as a part
	of the Replication set and the ports to which they listen to
	Example usage:

	```bash 
	cms pi mongo start --type=replica --master=blue --workers=blue00[1-3] \
	--port=2705[1-3]
	```
Run a test on your setup cluster   

```bash 
cms pi mongo test 
```
This command creates a mongod instance listening to the localhost and then asks
it to print the server status.
