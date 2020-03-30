# Setting up a Pi Spark Cluster

We assume you have installed cloudmesh as discussed in the

* [Pi Cloudmesh Instalation Guide](/README.md#installation)


TODO: This is not yet working and under development

The list of spark related commands are:

```
cms pi spark setup --master=MASTER --workers=WORKERS
cms pi spark start --master=MASTER --workers=WORKERS
cms pi spark stop --master=MASTER --workers=WORKERS
cms pi spark test --master=MASTER --workers=WORKERS
cms pi spark check [--master=MASTER] [--workers=WORKERS]
cms pi script list spark [--details]
```


## Usage

Let us assume we like to create a cluster with 3 workers and a master.
let us chose the work *red* as the prefix to the hostnames. Let us assume you burned them with cm burner and the hostnames are
*red*, *red01*, *red02*, *red03*.


Then the cluster can be set upi with

```
cms pi spark setup --master=red --workers="red[01-03]"
```

To make sure the setup succeded, use the command

```
cms pi spark check --master=red --workers="red[01-03]"
```

To start the cluster use

```
cms pi spark start --master=red --workers="red[01-03]"
```

Now you can run yoru spark programs. A simple test is avalable when you run

```
cms pi spark start --master=red --workers="red[01-03]"
```

To stop the cluster you can use

```
cms pi spark start --master=red --workers="red[01-03]"
```


## Script details

Cloudmesh pi contains a convenient mechanism to start scripts remotely
on a number of PI's in parallel.

The script names for the spark deploymnets can  be retrieved with

```
cms pi script list spark
```

To see the details of the script, pleas use

```
cms pi script list spark --details
```