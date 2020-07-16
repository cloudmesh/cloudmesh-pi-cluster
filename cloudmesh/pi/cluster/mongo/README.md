# Setting up a Pi MongoDB Cluster
**NOTE**: We are using the 32-bit Raspbian Buster operating system for our Pi cluster. Unfortunately, MongoDB only supports the legacy 2.4.14 version for a 32-bit operating system. Hence the MongoDB version deployed will be an older version which is no longer supported. Also, 32-bit builds of MongoDB are limited to less than 2GB of data. 

## Prerequisites

The master and workers must be set up as described in the general setup section. The worker Pis have to be connected to the internet via the master using the ```cms bridge``` command. The documentation for the command can be found here:

<https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/bridge>

## Installation
This following command will install MongoDB to the master and workers provided.

```
master$ cms pi mongo install [--master=MASTER] [--workers=WORKERS]
```

## Other Available Commands

Uninstall MongoDB on the master and/or any worker. This will also remove all of the installed dependancies.  
```
master$ cms pi mongo uninstall [--master=MASTER] [--workers=WORKERS]
```

Start the mongod client. The mongod client can start in one of two implementations depending on the ```--type``` argument provided. If the ```--type``` argument is not specified then the ```local``` option will be considered by default.  

```
master$ cms pi mongo start [--type=TYPE] [--master=MASTER] [--port=PORT] [--dbpath=DBPATH] [--ip_bind=IP_BIND]
```

1. ```--type=local```  
The mongod client will be launched on the master Pi only. The ```--port``` and ```--dbpath``` arguments may be provided if you want to specify the port and the database path respectively. If not provided, the values will default to ```--port=27014``` and ```--dbpath=\data\db```

2. ```--type=replica``` 
The mongod client will be launched in a Replication Set configuration. Currently, this command only supports launching a replica set in an odd configuration only with 3 Workers acting as secondary and 1 Master as primary. Providing the ```--master``` argument is necessary.

Run a test on your setup cluster   

```
master$ cms pi mongo test [--master=MASTER] [--workers=WORKERS]
```
