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

The list of spark related commands are:

```
cms pi spark check [--master=MASTER] [--workes=WORKERS]
cms pi spark setup [--master=MASTER] [--workers=WORKERS]
cms pi spark start --master=MASTER
cms pi spark stop --master=MASTER
cms pi spark test --master=MASTER
cms pi script list spark [--details]
cms pi spark uninstall --master=MASTER [--workers=WORKERS]
```

## Usage

Following example is a cluster with 3 workers and one master.
We'll use the word *red* as the prefix to the hostnames. We assume you
 burned them with cms pi burn create command and the hostnames are
*red*, *red001*, *red002*, *red003*.

##  Pi Spark Cluster Setup workflow


Optional: Perform a check step on Pis
```
cms pi spark check --master=red --workers="red[001-003]" 
```

You can setup the master and all your workers in one step or individually

### One step setup approach

```
cms pi spark setup --master=red --workers="red[001-003]" 
```

To-do:  eliminate the following warning commands.   They are a
 result of
 the program controlling the code in parallel across the worker Pis not liking
  the 'Y' pipe to
  install Java and Scala; however, without the 'Y' pipe, code freezes waiting
   for
   a reply.  These commands will likely repeat several times; if you wait, the
    command
    line
    will come back and
    install will be
    complete.
   
    debconf: unable to initialize frontend: Dialog
    debconf: (Dialog frontend will not work on a dumb terminal, an emacs shell buffer, or without a controlling terminal.)
    debconf: falling back to frontend: Readline
    debconf: unable to initialize frontend: Readline
    debconf: (This frontend requires a controlling tty.)
    debconf: falling back to frontend: Teletype
    dpkg-preconfigure: unable to re-open stdin:
    debconf: unable to initialize frontend: Dialog

### Multi-step approach
Step 1:  Setup master

```
cms pi spark setup --master=red 
```
** After running above command, exit master and log back in to run ~/bashrc
 and set system parameters **


Step 2: Add individual workers to the Spark cluster using:

```
cms pi spark setup --workers=red001 
```

### Test the Spark setup

Following command starts the cluster, runs an example Spark script and then
 stops the cluster.
 
 ***Prior to starting Spark test, exit from your master and log back in to
  ensure
  system variables are set correctly***
 
```
cms pi spark test --master=red
```
NOTE: If your master has a **password**, you'll be asked to enter it both in
 starting and stopping the cluster, but
 the requests
 may not be easily seen, due to other messages.
 
 There are many messages that scroll by; look for something along the lines of
 
 Job 0 finished: reduce at SparkPi.scala:38, took 1.971870 s
 
Pi is roughly 3.1469378673446684


### To start the cluster

```
cms pi spark start --master=red
```

### To stop the cluster

```
cms pi spark stop --master=red
```

### Uninstall Spark

```
cms pi spark uninstall --master=red --workers="red[001-003]"
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

## Spark console for executing command

$ spark-shell

    Spark context Web UI available at http://10.1.1.1:4040
    Spark context available as 'sc' (master = local[*], app id = local-1589031487342).
    Spark session available as 'spark'.
    Welcome to
          ____              __
        / __/__  ___ _____/ /__
        _\ \/ _ \/ _ `/ __/  '_/
        /___/ .__/\_,_/_/ /_/\_\   version 2.4.5
        /_/

    Using Scala version 2.11.12 (OpenJDK Server VM, Java 11.0.7)
    Type in expressions to have them evaluated.
    Type :help for more information.

    scala> 2+2
    res0: Int = 4

    scala> :q

## Pi Spark setup with shell programs as precursor to above

See README.Script.md
in cloudmesh=pi-cluster/cloudmesh/pi/cluster/spark/

Website with information <https://www.educba.com/how-to-install-spark/>


 
