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

Now you can run your spark programs. A simple test is available when you run

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

Website with information <https://www.educba.com/how-to-install-spark/>


 ## Prerequisites for Spark
 
 In order to use cloudmesh-spark, we first set up the Pi master. This
  includes installing Java, Scala and Spark and adding variables to /.bashrc
   so they are available via the terminal
   
 See the shell script files in the directory
  cloudmesh-pi-cluster/cluster/spark/bin/

## Setup using shell scripts
 
 To use the shell program approach:
 1) Create ~/spark-bashrc.txt
 2) Create /bin/spark-setup.sh
 3) Create /bin/spark/spark-copy-spark-to-worker.sh
 4) Create /binspark-setup-worker.sh
 5) Create /bin/spark-run-cluster-test.sh
 6) Create /bin/spark-uninstall2.4.5.sh
 

### On Master (green) ran the following:

```bash
sh /bin/spark-setup.sh
```

 ### Setup the Worker (green003)
 **Following are actual steps used in setting up worker green003**

    sh /bin/spark-copy-spark-to-worker.sh  

Which included this detail:

    #!/usr/bin/env bash
    scp /bin/spark-setup-worker.sh pi@green003:
    scp ~/spark-bashrc.txt pi@green003:
    scp /bin/spark-uninstall2.4.5.sh pi@green003:
    scp ~/sparkout.tgz pi@green003:
    ssh pi@green003 sh ~/spark-setup-worker.sh
    sudo cat >> $SPARK_HOME/conf/slaves << EOF
    pi@green003
    EOF

Received this error:

    7: /bin/spark-scp-setup-to-worker.sh: cannot create /home/pi/spark-2.4.5-bin-hadoop2.7/conf/slaves: Permission denied
 
 So made the change to slaves file on master manually
 
  
 ## Test the Master & Worker setup with a Spark test
 
 Spark test run
    
    #Start Spark cluster
    (ENV3) pi@green:~ $ sh $SPARK_HOME/sbin/start-all.sh


    starting org.apache.spark.deploy.master.Master, logging to /home/pi/spark-2.4.5-bin-hadoop2.7/logs/spark-pi-org.apache.spark.deploy.master.Master-1-green.out
    pi@localhost's password: pi@green002: starting org.apache.spark.deploy.worker.Worker, logging to /home/pi/spark-2.4.5-bin-hadoop2.7/logs/spark-pi-org.apache.spark.deploy.worker.Worker-1-green002.out
    pi@green001: starting org.apache.spark.deploy.worker.Worker, logging to /home/pi/spark-2.4.5-bin-hadoop2.7/logs/spark-pi-org.apache.spark.deploy.worker.Worker-1-green001.out
    pi@green003: starting org.apache.spark.deploy.worker.Worker, logging to /home/pi/spark-2.4.5-bin-hadoop2.7/logs/spark-pi-org.apache.spark.deploy.worker.Worker-1-green003.out

    localhost: starting org.apache.spark.deploy.worker.Worker, logging to /home/pi/spark-2.4.5-bin-hadoop2.7/logs/spark-pi-org.apache.spark.deploy.worker.Worker-1-green.out
    
    #Run the Spark test script   
    (ENV3) pi@green:~ $ $SPARK_HOME/bin/run-example SparkPi 4 10

    
 Output of Spark test script included:
 
    20/04/30 16:42:54 INFO DAGScheduler: Job 0 finished: reduce at SparkPi.scala:38, took 1.953871 s
    Pi is roughly 3.143637859094648  
    
Stopping Spark cluster

    (ENV3) pi@green:~ $ sh $SPARK_HOME/sbin/stop-all.sh

    pi@localhost's password: pi@green001: stopping org.apache.spark.deploy.worker.Worker
    pi@green003: stopping org.apache.spark.deploy.worker.Worker
    pi@green002: stopping org.apache.spark.deploy.worker.Worker

    localhost: stopping org.apache.spark.deploy.worker.Worker
    stopping org.apache.spark.deploy.master.Master
    /home/pi/spark-2.4.5-bin-hadoop2.7/sbin/stop-all.sh: 34: [: unexpected operator
    (ENV3) pi@green:~ $
    
    
## Following are the shell and text files.  

See <https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/cluster/spark/bin>
 
 spark-setup.sh
 
 ```bash
#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install default-jdk
sudo apt-get install scala
cd ~
sudo wget http://mirror.metrocast.net/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz -O sparkout.tgz
sudo tar -xzf sparkout.tgz
cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
sudo cp ~/.bashrc ~/.bashrc-backup
sudo cp ~/temp-bashrc ~/.bashrc
sudo rm ~/temp-bashrc
sudo chmod 777 ~/spark-2.4.5-bin-hadoop2.7/conf
sudo cp /home/pi/spark-2.4.5-bin-hadoop2.7/conf/slaves.template /home/pi/spark-2.4.5-bin-hadoop2.7/conf/slaves
```

 spark/spark-copy-spark-to-worker.sh
  ```bash
#!/usr/bin/env bash
scp ~/spark-bashrc.txt pi@green001:
scp /bin/spark-uninstall2.4.5.sh pi@green001:
scp /bin/spark-setup-worker.sh pi@green001:
scp ~/sparkout.tgz pi@green001:
ssh pi@green001 sh ~/spark-setup-worker.sh
sudo cat >> $SPARK_HOME/conf/slaves << EOF
pi@green001
EOF
```

spark-setup-worker.sh
  ```bash
#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install default-jdk
sudo apt-get install scala
cd ~
sudo tar -xzf sparkout.tgz
cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
sudo cp ~/.bashrc ~/.bashrc-backup
sudo cp ~/temp-bashrc ~/.bashrc
sudo rm ~/temp-bashrc
sudo chmod 777 ~/spark-2.4.5-bin-hadoop2.7/
```


spark-bashrc.txt

  ```bash
#JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
#SCALA_HOME
export SCALA_HOME=/usr/share/scala
export PATH=$PATH:$SCALA_HOME/bin
#SPARK_HOME
export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin
```
spark-uninstall2.4.5.sh

  ```bash
#!/usr/bin/env bash
sudo apt-get remove openjdk-11-jre
sudo apt-get remove scala
cd ~
sudo rm -rf spark-2.4.5-bin-hadoop2.7
sudo rm -f sparkout.tgz
sudo cp ~/.bashrc-backup ~/.bashrc
```

spark-run-cluster-test.sh
  ```bash
#!/usr/bin/env bash
sh $SPARK_HOME/sbin/start-master.sh
sh $SPARK_HOME/sbin/start-slaves.sh
#Test program:
$SPARK_HOME/bin/run-example SparkPi 4 10
sh $SPARK_HOME/sbin/stop-all.sh
```


