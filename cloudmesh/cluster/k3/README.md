# Install

You must first set up your workers to connect to the internet through
your master. This is done by using the command ```cms bridge```. You can
find the documentation here to set it up:
<https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/bridge>

**Note**: The install command currently works by setting up Kubernetes
*on your master and workers, but is having issues adding the worker
*nodes to the master cluster. Fix coming soon.

```
master$ cms pi k3 install [--master=MASTER] [--workers=WORKERS]
```

**Note**: If you have never enabled containers on your raspberry pis
*before, please look at the first option listed below

## Other options for install

Enabling Containers: For Kubernetes to work, you must enable containers.
To do this, append the following command to the install command above to
enable containers on the master and workers you list.

```
master$ cms pi k3 install [--master=MASTER] [--workers=WORKERS] --step=enable_containers
```

## Other Available Commands

Join a worker to the master's cluster if Kubernetes is already installed on the node 

```
master$ cms pi k3 join --workers=WORKERS
```

Uninstall Kubernetes on either the master or any worker

```
master$ cms pi k3 uninstall [--master=MASTER] [--workers=WORKERS]
```

Delete a node(s) from your master's cluster

```
master$ cms pi k3 delete [--master=MASTER] [--workers=WORKERS]
```

Run a test on your setup cluster **(Not yet implemented)**

```
master$ cms pi k3 test [--master=MASTER] [--workers=WORKERS]
```

View details about your cluster:

```
master$ cms pi k3 view
```
