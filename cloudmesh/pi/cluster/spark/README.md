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
** After running above command, exit master and log back in to run ~/bashrc
 and set system parameters **

Step 2: Ensure master setup succeeded, use command
```
cms pi spark test --master=red
```
If your master has a password, you'll be asked to enter it, but the command
 may not be easily seen, due to following messages.


Step 3: Add individual workers to the Spark cluster using:

```
cms pi spark setup --workers=red001 
```

Work in progress setting up multiple workers automatically from cms command
.  For now, repeat the above commands for each worker name.

Step 4: Confirm worker(s) added 
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


  
    #     # Setup the Pi master with the prerequisite applications
    #       shell script "spark.prereqs"
    #
    #     # Download Spark on the Pi master
    #       shell script "spark.download.spark"
    #
    #     # Install spark on Pi master
    #       shell script "spark.install"
    #
    #     # Update Pi master's ~/.bashrc file and prepare environment for workers
    #       shell script "spark.bashrc.master"
    #
    #     # Setup a Pi worker by copying files from Pi master to Pi worker & executing a shell file on worker
    #
    #     # Update slaves file on master
    #       function update_slaves(self)

           

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


 
