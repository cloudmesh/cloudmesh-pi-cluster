# Setting up a Pi Spark Cluster

Prerequisites include installing cloudmesh as discussed in the installation
 guide below:

* [Pi Cloudmesh Installation Guide](/README.md#installation)

Cloudmesh system (cms) commands are used to burn the Raspberry Pi Master and Pi
 Worker SD
 cards, create a bridge enabling workers to access Internet throught master and
  also to install various
  cluster management systems for comparison.
    
  Steps below describe installing **Apache Spark** on a Raspberry Pi
   cluster
   having a Master
  Pi and one or many Worker Pis, i.e., 1 to 100.
  

Shell scripts are automated and integrated into the following cms commands

TODO: **This is under testing**

The list of spark related commands are:

```
cms pi spark setup --master=MASTER --workers=WORKERS
cms pi spark start --master=MASTER --workers=WORKERS
cms pi spark stop --master=MASTER --workers=WORKERS
cms pi spark test --master=MASTER --workers=WORKERS
cms pi script list spark [--details]
```

## Usage

Following example is a cluster with 3 workers and one master.
We'll use the word *red* as the prefix to the hostnames. We assume you
 burned them with cms pi burn create command and the hostnames are
*red*, *red001*, *red002*, *red003*.

##  Pi Spark Cluster Setup workflow

Below are the automated workflow steps and scripts integrated into cms
 commands for installing and testing a Spark installation with one master and
  one worker on a Pi
  Cluster.


    #     # Setup the Pi master with Spark (Java & Scala) applications
    #       script "spark.setup.master"
    #
    #     # Update the Pi master's ~/.bashrc file
    #       function update_bashrc(self)
    #
    #     # Create a shell file on Pi master to run on Pi worker
    #       function create_spark_setup_worker(self)
    #
    #     # Create a file on Pi master that will be copied to and append to ~/.bashrc on Pi worker
    #       function create_spark_bashrc_txt
    #
    #     # Copy shell and bashrc change files to Pi workers, execute shell file on Pi worker
    #       script "copy.spark.to.worker"
    #
    #     # Update slaves file on master
    #       function update_slaves(self)

Setting up multiple workers and one master in one command is an objective, not yet
 implemented

Master is setup with

```
cms pi spark setup --master=red 
```

To ensure setup succeeded, use command

```
cms pi spark test --master=red"
```

To start the cluster use

```
cms pi spark start --master=red"
```

To stop the cluster use

```
cms pi spark stop --master=red"
```

Individual workers are setup using:

```
cms pi spark setup --workers=red001 
```

Work in progress setting up multiple workers automatically from cms command

## Script details

Cloudmesh pi contains convenient mechanisms to start scripts remotely

Script names for the spark deploymnets can  be retrieved with

```
cms pi script list spark
```

To see the details of the script, pleas use

```
cms pi script list spark --details
```


# Appendix details

## Pi Spark setup with shell programs as precursor to above

See README.Script.md
in cloudmesh=pi-cluster/cloudmesh/pi/cluster/spark/

Website with information <https://www.educba.com/how-to-install-spark/>


 
