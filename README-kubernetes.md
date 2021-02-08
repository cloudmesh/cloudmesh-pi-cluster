# Cloudmesh Kubernetes

## Install

You must first set up your workers to connect to the internet through
your manager. This is done by using the command ```cms bridge```. You can
find the documentation here to set it up:

* <https://github.com/cloudmesh/cloudmesh-pi-cluster/README.md>

This command will install Kubernetes to the manager and workers you provide, 
and will join the workers to your manager's cluster.

```
manager$ cms pi k3 install [--master=MASTER] [--workers=WORKERS]
```

**Note**: If you have never enabled containers on your raspberry pis
*before, please look at the first option listed below

## Other options for install

Enabling Containers: For Kubernetes to work, you must enable containers.
To do this, append the following command to the install command above to
enable containers on the manager and workers you list.

```
manager$ cms pi k3 install [--master=MASTER] [--workers=WORKERS] --step=enable_containers
```

## Other Available Commands

Join a worker to the manager's cluster if Kubernetes is already installed on the node 

```
manager$ cms pi k3 join --workers=WORKERS
```

Uninstall Kubernetes on either the manager or any worker

```
manager$ cms pi k3 uninstall [--master=MASTER] [--workers=WORKERS]
```

Delete a node(s) from your manager's cluster

```
manager$ cms pi k3 delete [--master=MASTER] [--workers=WORKERS]
```

Run a test on your setup cluster **(Not yet implemented)**

```
manager$ cms pi k3 test [--master=MASTER] [--workers=WORKERS]
```

View details about your cluster:

```
manager$ cms pi k3 view
```
