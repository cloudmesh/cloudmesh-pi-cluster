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
cms pi spark setup [--master=MASTER] [--workers=WORKERS]
cms pi spark start --master=MASTER
cms pi spark stop --master=MASTER
cms pi spark test --master=MASTER
cms pi script list spark [--details]
```

## Usage

Following example is a cluster with 3 workers and one master.
We'll use the word *red* as the prefix to the hostnames. We assume you
 burned them with cms pi burn create command and the hostnames are
*red*, *red001*, *red002*, *red003*.

##  Pi Spark Cluster Setup workflow


Step 1:  Setup master

```
cms pi spark setup --master=red 
```
** Logout of master and log back in to run ~/bashrc and set system parameters **

Step 2: Ensure master setup succeeded, use command

```
cms pi spark test --master=red
```

Step 3: Setup individual workers using:

```
cms pi spark setup --workers=red001 
```

Work in progress setting up multiple workers automatically from cms command

Step 4: Confirm worker added 
by repeating Step 2

```
cms pi spark test --master=red"
```
Step 5: Start the cluster

```
cms pi spark start --master=red"
```

Step 6: Stop the cluster

```
cms pi spark stop --master=red"
```
Behind the cms commands are automated workflow steps and scripts integrated
 into cms
 commands for installing and testing a Spark installation with one master and
  one worker on a Pi
  Cluster.  
  
  The shell scripts and functions described next are housed in cloudmesh-pi
  -cluster/cloudmesh/pi/cluster/spark/spark.py


    #     # Setup the Pi master with Spark (Java & Scala) applications
    #       shell script "spark.setup.master"
    #
    #     # Update the Pi master's ~/.bashrc file
    #       python function update_bashrc()
    #
    #     # Create a shell file on Pi master to run on Pi worker
    #       python function create_spark_setup_worker()
    #
    #     # Create a file on Pi master that will be copied to and append to ~/.bashrc on Pi worker
    #       python function create_spark_bashrc_txt()
    #
    #     # Copy shell and bashrc change files to Pi workers, execute shell file on Pi worker
    #       shell script "copy.spark.to.worker"
    #
    #     # Update slaves file on master
    #       python function update_slaves()
    #
    #     # Test Spark cluster
    #       shell script "spark.test"
    #
    #     # Start Spark cluster
    #       shell script "spark.start"
    #
    #     # Stop Spark cluster
    #       shell script "spark.stop"
    #
           

Setting up multiple workers and one master in one command is an objective, not yet
 implemented

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


 
