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


# Appendix details

## Pi Spark setup with shell programs as precursor to above

 ## Prerequisites for Spark
 
 In order to use cloudmesh-spark, we first set up the Pi master. This
  includes installing Java, Scala and Spark and adding variables to /.bashrc
   so they are available via the terminal
   
 See the shell script files for setting up the master in the directory
  cloudmesh-pi-cluster/cluster/spark/bin/

## Setup the Master

First, install the necessary software on the Master (Java, Scala, Spark), see
 spark-setup.sh.  Second, update /home/pi/.bashrc, see spark-bashrc.sh.   Then
 , update spark-env.sh in the spark/conf directory.

```bash
sh /bin/spark-setup.sh
sh /bin/spark-bashrc.sh
sh /bin/spark-env.sh.setup.sh
```
To ensure workers are setup the same as the master, the master's setup is
 zipped in order to copy to each worker.

```bash
sh /bin/spark-save-master.sh
```

The zipped directory files are copied to the worker 

```bash
sh /bin/spark-scp-files-to-worker.sh
```
A shell file executed from the master finishes
 the worker set up. An ssh command on the master, executes a
  shell program (spark-setup
-worker.sh) on the
 worker (yellow-002) 
 remotely. 
  
```bash
ssh yellow-002 sh ~/spark-setup-worker.sh
```

These shell programs will be put into python program for including in cms.

Note: nmap is suggested by one of the sites for managing clusters.  Installed
 but haven't used it. 
  (ENV3) pi@yellow:~ $ pip install nmap
Successfully installed nmap-0.0.1
 
 
 ## Setup the Worker (an example)
 **Following are actual steps used in setting up worker green001**
 
 Copied files from cloudmesh-pi-cluster/cloudmesh/cluster/spark/bin/ into pi
 @green: /bin/
 
    (ENV3) pi@green:~ $ sudo nano ~/spark-setup-worker.sh
    (ENV3) pi@green:/bin $ sudo nano spark-bashrc.sh  
    (ENV3) pi@green:/bin $ sudo nano spark-env-sh-setup.sh 
    
    (ENV3) pi@green:~ $ sudo nano /bin/spark-scp-files-to-worker.sh 

    Batch file problems:
    1) bashrc file is getting updated wrong, too many directories in path, $PATH
     question
     
    2) unable to edit the spark-env.sh file from script
    
    #This executes the secure copy (scp) steps above
    (ENV3) pi@yellow:~ $ sh /bin/spark-scp-files-to-worker.sh


After running above, all the needed files are on the worker, but they aren't
 in the right file or directory locations.   Therefore, need to run the
  following
  command from
  the master to start the shell scripts on the worker (yellow-001) 
 
    ssh yellow-001 sh ~/spark-setup-worker.sh
   
Then, yellow-001 was added to the following file on the master

    sudo nano /usr/local/spark/spark/conf/slaves
 
 ## Test the Master & Worker setup with a Spark test
 
Followed by the Spark test run
    
    #Start Spark cluster
    (ENV3) pi@yellow:~ $ /usr/local/spark/spark/sbin/start-all.sh 
    
    #Run the Spark test script   
    (ENV3) pi@yellow:~ $ /usr/local/spark/spark/bin/run-example SparkPi 4 10  
    
 Output of Spark test script included:
 
    2020-04-19 22:22:21 INFO  DAGScheduler:54 - Job 0 finished: reduce at
    SparkPi.scala:38, took 2.315185 s
    Pi is roughly 3.142117855294638    
    
Stopping Spark cluster

    (ENV3) pi@yellow:~ $ /usr/local/spark/spark/sbin/stop-all.sh
    
    pi@localhost's password: 
    yellow-001: stopping org.apache.spark.deploy.worker.Worker
    yellow-003: stopping org.apache.spark.deploy.worker.Worker
    yellow-002: stopping org.apache.spark.deploy.worker.Worker
    localhost: stopping org.apache.spark.deploy.worker.Worker
    stopping org.apache.spark.deploy.master.Master
    
    
## Following are the shell files.  

See sp20-516-246/pi_spark/bin directory
 
 spark-setup.sh
 
 ```bash
#!/usr/bin/env bash
sudo apt-get install openjdk-8-jre
sudo apt-get install scala
cd /usr/local/spark
sudo wget http://apache.osuosl.org/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz -O sparkout2-3-4.tgz
sudo tar -xzf sparkout2-3-4.tgz
```

 spark-bashrc.sh
 
 cat ~/.bashrc
 
 ```bash
#!/usr/bin/env bash
cat >> ~/.bashrc << EOF
#SCALA_HOME
export SCALA_HOME=/usr/share/scala
export PATH=$PATH:$SCALA_HOME/bin
#SPARK_HOME
export SPARK_HOME=/usr/local/spark/spark
export PATH=$PATH:$SPARK_HOME/bin
EOF
```

 spark-env-sh-setup.sh
 
 ```bash
#!/usr/bin/env bash
cat >> /usr/local/spark/spark/conf/spark-env.sh << EOF
#JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
EOF
```
spark-save-master.sh
 
 ```bash
#!/usr/bin/env bash
cd /usr/share/scala-2.11
sudo tar -cvzf scalaout2-11.tar.gz *
cd /usr/lib/jvm/java-8-openjdk-armhf
sudo tar -cvzf javaout8.tgz *
cd /usr/local/spark/spark
sudo tar -cvzf sparkout.2-3-4.tgz *
```
spark-scp-files-to-worker.sh
 
 ```bash
#!/usr/bin/env bash
scp -r $SCALA_HOME/scalaout2-11.tar.gz pi@yellow-001:
scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz pi@yellow-001:
scp -r /usr/local/spark/spark/sparkout.2-3-4.tgz pi@yellow-001:
scp -r ~/spark.setup.worker.sh pi@yellow-001:
scp -r ~/spark-env.sh.setup.sh pi@yellow-001:                        
scp -r ~/spark-bashrc.sh pi@yellow-001:
```
spark-setup-worker.sh

 ```bash
#!/usr/bin/env bash
cd /usr/lib
sudo mkdir jvm
cd jvm
sudo mkdir java-8-openjdk-armhf
sudo mv ~/javaout8.tgz /usr/lib/jvm/java-8-openjdk-armhf/
cd /usr/lib/jvm/java-8-openjdk-armhf
sudo tar -xvzf javaout8.tgz
cd /usr/share
sudo mkdir /usr/share/scala-2.11
sudo mv ~/scalaout2-11.tar.gz /usr/share/scala-2.11/
cd /usr/share/scala-2.11
sudo tar -xvzf scalaout2-11.tar.gz
cd /usr/local
sudo mkdir spark
cd /usr/local/spark
sudo mkdir spark
cd /usr/local/spark/spark
sudo mv ~/sparkout.2-3-4.tgz /usr/local/spark/spark/
cd /usr/local/spark/spark
sudo tar -xvzf sparkout.2-3-4.tgz
sh ~/spark-env.sh.setup.sh                        
sh ~/spark-bashrc.sh
```


## Starting Spark

Within the Master's spark directory and conf folder is a slaves file indicating
 the workers
```lines
sudo nano /usr/local/spark/spark/conf/slaves
```

add following lines to slaves file:

```lines
localhost
yellow-001
yellow-002
yellow-003
yellow-004
```

Start master and then slave from master command line

```command lines
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slaves.sh
```

Run a test script on the cluster
```bash
$ cd /usr/local/spark/spark/bin 
$ run-example SparkPi 4 10
``` 

Then stop master and slave
```bash
$SPARK_HOME/sbin/stop-master.sh
$SPARK_HOME/sbin/stop-slaves.sh
```
### Setting up keys

In order to get passwordless access to workers from master:

spark-ssh-setup.sh
```bash
#!/usr/bin/env bash
eval $(ssh-agent)
ssh-add
```


