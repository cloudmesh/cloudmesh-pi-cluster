# Setting up a Pi Hadoop Cluster

# Hadoop Clusters with Raspberry Pi Jessica Zhu sp20-516-252

Reference for setup:

<https://github.com/cloudmesh/cloudmesh-pi-burn>
<https://github.com/cloudmesh/cloudmesh-pi-cluster>
<https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/master/cloudmesh/bridge/README.md>

For the numpy issue:
<https://github.com/numpy/numpy/issues/14348>


Master and workers are burnt using `cloudmesh-pi-cluster`.
    master: pi@red
    workers: red[001 - 002]

and bridge has been properly created.

## install Java on master and workers

Hadoop requires Java. Raspbian Desktop doesn't come with Java installed
, we therefore need to install java on all of the Pi.

### Install Java on master node

```
cd ~
git clone https://github.com/cloudmesh-community/sp20-516-252.git
cd sp20-516-252/pi_hadoop/bin
echo "Y" | sh setup-master.sh
```

Check if the java and jps installation is successful by running
`
$ java -version
$ jps
`

It should expect return
```
openjdk version "1.8.0_212"
OpenJDK Runtime Environment (build 1.8.0_212-8u212-b01-1+rpi1-b01)
OpenJDK Client VM (build 25.212-b01, mixed mode)

11630 Jps
```

### Install Java on worker nodes

Since workers don't have access to network, java can be installed by master
 passing the installation package to workers.
 
 Ensure you can ssh into workers without password
 ```buildoutcfg
$ ssh red001
$ ssh red002
```
 
 run command 
  ```
sh master-to-worker.sh
```

Now that each worker has the right java zip package, we are gonna upzip and
 install java on each worker using just one line from master:
 
 This py file is in cloudmesh-common (this JobMultiHostScript.py needs to be
  motified till the source code is fixed)
 ```
cd ~/cm/cloudmesh-common/cloudmesh/common
sudo nano JobMultiHostScript.py
```
 ```
 import sys
 
 def main():
    # EXAMPLE FOR TERMINAL - python JobMultiHostScript.py [SCRIPT-FILE] [HOSTS]
    argumentCounter = 0
    for arg in sys.argv[1:]:
        # Script file
        if argumentCounter == 0:
            scriptFile = arg
        # Get hosts
        else:
            hosts = arg
        argumentCounter = argumentCounter + 1
    with open(scriptFile) as f:
        script = f.readlines()
    script = ''.join(script)
    hosts = Parameter.expand(hosts)
    result = JobMultiHostScript.execute(script, "terminal_script", hosts)
if __name__ == '__main__':
    main()
    """script =
    # This is a comment
    # Task: pwd
    pwd     # tag: pwd
    # Task:  uname
    uname -a
    "";
    hosts = Parameter.expand("purple[01-02]")
    result = JobMultiHostScript.execute(script, "script_name", hosts,
                                        beginLine="# Task: pwd", endLine="# Task: uname")
    """

 ```
 
 `python JobMultiHostScript.py ~/sp20-516-252/pi_hadoop/bin/worker-installation.sh red[001-002]`

If it is installed successfully on workers, you should see returns similar to
 this. Basically, stdout shouldnt tell you there is any error.
 
```
{'red001': {'command': 'java -version',
            'host': 'red001',
            'name': 'red001',
            'returncode': 0,
            'status': 'done',
            'stderr': '',
            'stdout': b''},
 'red002': {'command': 'java -version',
            'host': 'red002',
            'name': 'red002',
            'returncode': 0,
            'status': 'done',
            'stderr': '',
            'stdout': b''}}
```

## Install Hadoop on Master Node (on file)

```buildoutcfg
$ sh ~/sp20-516-252/pi_hadoop/bin/install-hadoop-master.sh
$ source ~/.bashrc
$ cd && hadoop version | grep Hadoop
$ sh ~/sp20-516-252/pi_hadoop/bin/install-hadoop-master2.sh
```


Below compressed 
-----------------
Download and install Hadoop version 3.2.0
```
$ cd ~
$ wget https://archive.apache.org/dist/hadoop/common/hadoop-3.2.0/hadoop-3.2.0.tar.gz
$ sudo tar -xvzf hadoop-3.2.0.tar.gz -C /opt/
$ cd /opt/
$ sudo mv hadoop-3.2.0 hadoop
```
Change permission on the directory
```buildoutcfg
sudo chown pi:pi -R /opt/hadoop
```


Set up Environment. Edit `~/.bashrc` and append the following lines
```buildoutcfg
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

Then apply the changes to the running environment
```
$ source ~/.bashrc
```

Now set up Hadoop environment by editing `$ /opt/hadoop/etc/hadoop/hadoop-env.sh`
Add the line below to the end of the file
```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf
```
If you are unsure where your JAVA_HOME path is, simply try 
`dirname $(dirname $(readlink -f $(which javac)))`
, which returns HOME_PATH.

Now check if Hadoop has been successfully installed
```buildoutcfg
cd && hadoop version | grep Hadoop
```
You should expect `Hadoop 3.2.0`

## Starting Hadoop (below no on file)

```buildoutcfg
$ sh ~/sp20-516-252/pi_hadoop/bin/master-start-hadoop.sh
$ source ~/.bashrc
```
--compile code below

Set environment variables. Add to the end of `~/.bashrc`
```buildoutcfg
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
```
Then `source ~/.bashrc`


-----


Setup Hadoop Configuration Files
```
$ sh ~/sp20-516-252/pi_hadoop/bin/master-hadoop-config.sh
```

--- Below compressed


Edit core-site.xml

```
<configuration>
<property>
  <name>fs.default.name</name>
    <value>hdfs://red:9000</value>
</property>
</configuration>
```

Edit hdfs-site.xml

```
<configuration>
<property>
 <name>dfs.replication</name>
 <value>1</value>
</property>

<property>
  <name>dfs.name.dir</name>
    <value>file:///opt/hadoop/hadoopdata/hdfs/namenode</value>
</property>

<property>
  <name>dfs.data.dir</name>
    <value>file:///opt/hadoop/hadoopdata/hdfs/datanode</value>
</property>
</configuration>
```

Edit mapred-site.xml

```
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
<property>
 <name>yarn.app.mapreduce.am.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
<property>
 <name>mapreduce.map.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
<property>
 <name>mapreduce.reduce.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
</configuration>

```
Edit yarn-site.xml

```
<configuration>
 <property>
  <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
 </property>
</configuration>
```

---

Format Namenode

```
$ hdfs namenode -format
```

You should see lines like 
```buildoutcfg
...
2020-04-30 23:40:52,936 INFO common.Storage: Storage directory /opt/hadoop/hadoopdata/hdfs/namenode has been successfully formatted.
2020-04-30 23:40:52,978 INFO namenode.FSImageFormatProtobuf: Saving image file /opt/hadoop/hadoopdata/hdfs/namenode/current/fsimage.ckpt_0000000000000000000 using no compression
2020-04-30 23:40:53,276 INFO namenode.FSImageFormatProtobuf: Image file /opt/hadoop/hadoopdata/hdfs/namenode/current/fsimage.ckpt_0000000000000000000 of size 397 bytes saved in 0 seconds .
2020-04-30 23:40:53,325 INFO namenode.NNStorageRetentionManager: Going to retain 1 images with txid >= 0
2020-04-30 23:40:53,337 INFO namenode.NameNode: SHUTDOWN_MSG: 
/************************************************************
SHUTDOWN_MSG: Shutting down NameNode at red/127.0.1.1
************************************************************/

```

## start single node on master
First of all, get the permission, then we will start dfs

```
cd ~/.ssh
cat id_rsa.pub >> authorized_keys
cd $HADOOP_HOME/sbin/
./start-dfs.sh
```

You should see lines like below. You can ignore the WARN.
```buildoutcfg
Starting namenodes on [red]
Starting datanodes
Starting secondary namenodes [red]
2020-04-30 23:46:50,198 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable

```

Then start yarn, see the return
```buildoutcfg
$ ./start-yarn.sh
Starting resourcemanager
Starting nodemanagers
```

Then run `jps`. All these six items should be there. Missing any of them
 might cause failture of Hadoop work.

```buildoutcfg
$ jps
2736 NameNode
2850 DataNode
3430 NodeManager
3318 ResourceManager
3020 SecondaryNameNode
3935 Jps
```

Check the node online, type in `http://red:9870` on your web browser
You should see a web page showing resources.
`http://red:8088` shows nodes of the cluster. 

![red:9870_on_web](images/resource-manager-web.png)



## An example calculation pi using master

run the line below
```buildoutcfg
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.0.jar pi 2 5
```
Here we have set 
```buildoutcfg
number of maps = 2
Samples per Map = 5
```
You should get results similar to 
```buildoutcfg
...
Job Finished in 35.558 seconds
Estimated value of Pi is 3.60000000000000000000
```
Change to 
```buildoutcfg
Number of Maps  = 16
Samples per Map = 1000
```
You should expect a result with higher accuracy
```buildoutcfg
...
Job Finished in 64.2 seconds
Estimated value of Pi is 3.15000000000000000000
```

You can stop Hadoop by running 
```
./stop-all.sh
```

## create cluster with multiple Pi

# copy and install hadoop on workers

scp -r /home/pi/hadoop-3.2.0.tar.gz red001:
ssh red001
sudo tar -xvzf hadoop-3.2.0.tar.gz -C /opt/
sudo mv /opt/hadoop-3.2.0 /opt/hadoop
sudo chown pi:pi -R /opt/hadoop

# install jps
sudo nano ~/.bashrc
alias jps='/opt/jdk/bin/jps'
source ~/.bashrc
jps

# remove hdfs folder files on master

cd ~/opt/hadoop/hadoopdata/hdfs

# Set hadoop env on Worker

ssh red001
sudo nano  /opt/hadoop/etc/hadoop/hadoop-env.sh
   export JAVA_HOME=/opt/jdk/jre

core-site.xml

```
<configuration>
<property>
  <name>fs.default.name</name>
    <value>hdfs://red:9000</value>
</property>
</configuration>
```

hdfs-site.xml

```
<configuration>
<property>
 <name>dfs.replication</name>
 <value>2</value>
</property>

<property>
  <name>dfs.name.dir</name>
    <value>file:///opt/hadoop/hadoopdata/hdfs/namenode</value>
</property>

<property>
  <name>dfs.data.dir</name>
    <value>file:///opt/hadoop/hadoopdata/hdfs/datanode</value>
</property>
</configuration>

```

mapred-site.xml

```
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
<property>
 <name>yarn.app.mapreduce.am.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
<property>
 <name>mapreduce.map.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
<property>
 <name>mapreduce.reduce.env</name>
 <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
</property>
</configuration>
```

yarn-site.xml

```
<?xml version="1.0"?>

<configuration>
 <property>
  <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
 </property>
</configuration>
```
















------ Below gibberish ---

Change ownership of the destination folder, then paste the file to it
```buildoutcfg
ssh red001
chown pi /opt
scp -r /opt/hadoop red001:/opt
```

hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.0.jar pi 2 5

/opt/jdk/jre


--
sudo mkdir /usr/java/
tar -zxf packageName.tar.gz -C /usr/java

sudo update-alternatives --install /usr/bin/java java /usr/java/jre/bin/java 100
sudo update-alternatives --install /usr/bin/javac javac /usr/java/jre/bin/java 100

references
1. https://gist.github.com/filipelenfers/ef3f593deb0751944bb54b744bcac074
2. https://dev.to/awwsmm/building-a-raspberry-pi-hadoop-spark-cluster-8b2#hadoopspark
3. https://tecadmin.net/setup-hadoop-single-node-cluster-on-centos-redhat/