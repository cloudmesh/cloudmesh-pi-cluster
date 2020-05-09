## set up Hadoop Cluster

### install Java and Jps
 - Master
 
 Reference for setup:

<https://github.com/cloudmesh/cloudmesh-pi-burn>
<https://github.com/cloudmesh/cloudmesh-pi-cluster>
<https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/master/cloudmesh/bridge/README.md>

For the numpy issue:
<https://github.com/numpy/numpy/issues/14348>

```
$ echo "Y" | sudo apt install libatlas3-base libgfortran5
$ sudo pip3 install numpy
```

We assume to connection is `Laptop -> manager -> red/master -> all the workers`.

To go passwordless:

```
eval `ssh-agent -s` 
ssh-add
```

At the moment, you need to copy the public key of the master, then into
 workers in order to allow direct access to workers from the master. 

To ssh into master for the first time, on your own computer, do
`rm -f .ssh/known_hosts`

```
cd ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin
echo "Y" | sh setup-master.sh
```

Check if the java and jps installation is successful by running the commands
 below. The process number of jps might be different.
 
```
$ java -version
openjdk version "1.8.0_212"
OpenJDK Runtime Environment (build 1.8.0_212-8u212-b01-1+rpi1-b01)
OpenJDK Client VM (build 25.212-b01, mixed mode)
$ jps
11630 Jps
```
 
 - Nodes 

 run command 

```
cd /usr/lib/jvm/java-8-openjdk-armhf
# zip all the files
sudo tar -czf openjdkpkg.tgz *
# send over to worker node red001
scp -r /usr/lib/jvm/java-8-openjdk-armhf/openjdkpkg.tgz red001:
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
 
 `python JobMultiHostScript.py ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/worker-installation.sh red[001-002]`

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


in ~/.bashrc add line `export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf`
`source ~/.bashrc`

Check JAVA_HOME
`echo $JAVA_HOME`

 - install jps
 
```
nano ~/.bashrc
alias jps='/usr/lib/jvm/java-8-openjdk-armhf/bin/jps'
source ~/.bashrc
jps
```

### Install Hadoop

#### Install Hadoop on Master Node  

 - Master
 
```buildoutcfg
$ sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/install-hadoop-master.sh
$ source ~/.bashrc
$ sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/install-hadoop-master2.sh
$ cd && hadoop version | grep Hadoop
$ sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/master-start-hadoop.sh
$ source ~/.bashrc
$ sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/master-hadoop-config-cluster.sh
```

 - Worker

```
$ ssh red001
$ cd ~
$ wget https://archive.apache.org/dist/hadoop/common/hadoop-3.2.0/hadoop-3.2.0.tar.gz
# $ scp hadoop-3.2.0.tar.gz red002:~/
$ sudo tar -xvzf hadoop-3.2.0.tar.gz -C /opt/
$ cd /opt/
$ sudo mv hadoop-3.2.0 hadoop
$ sudo chown pi:pi -R /opt/hadoop
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
`echo $JAVA_HOME`
, which returns JAVA_HOME.

Now check if Hadoop has been successfully installed
```buildoutcfg
cd && hadoop version | grep Hadoop
```
You should expect `Hadoop 3.2.0`

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


Back to the master:
```buildoutcfg
$ scp /opt/hadoop/etc/hadoop/* red001:/opt/hadoop/etc/hadoop/
```

The `/opt/hadoop/etc/hadoop/worker` file should look like below on both master
 and worker nodes
 
```
localhost
red001
```

Lastly, on each node `/etc/hosts` should look like below
```
# 127.0.1.1 red   # ensure this line "123.0.1.1 <local hostname>" is removed/commented out   
10.1.1.4 red001   # IP can be different depending on what is assigned
10.1.1.3 red
```

### Run Hadoop Cluster 

Clean all the old data, and format Namenode

```
$ cd /opt/hadoop/hadoopdata/hdfs
$ sudo rm -rf *
$ hdfs namenode -format
```

First of all, get the permission, then we will start dfs. Ensure that every time
 to run a job, to have the cluster exit
 the safe mode. 

```
cat ~/.ssh/id_rsa.pub >>  ~/.ssh/authorized_keys
if permission demied: sudo chown pi:pi authorized_keys
cd $HADOOP_HOME/sbin/
Make changes on /etc/worker file on both master and worker
./start-dfs.sh
./start-yarn.sh
HADOOP_HOME/bin/hadoop dfsadmin -safemode leave
```

Currently the online web is unavailable to monitor cluster activities
. However, you can still check them, especially ensure that ALL nodes have
 been started, by running the line

```
hdfs dfsadmin -report
```

--- currently unavaialble
Check the node online, type in `http://red:9870` on your web browser
You should see a web page showing resources.
`http://red:8088` shows nodes of the cluster. 
