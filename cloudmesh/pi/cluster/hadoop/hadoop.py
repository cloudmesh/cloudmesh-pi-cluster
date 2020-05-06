import os
import textwrap
from pprint import pprint

from cloudmesh.pi.cluster.Installer import Installer
from cloudmesh.pi.cluster.Installer import Script
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner


class Hadoop:

    def execute(self, arguments):
        """
        pi hadoop setup --master=MASTER --workers=WORKER
        pi hadoop start --master=MASTER --workers=WORKER
        pi hadoop stop --master=MASTER --workers=WORKER
        pi hadoop test --master=MASTER --workers=WORKER
        pi hadoop check --master=MASTER --workers=WORKER

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        hosts = []
        if arguments.master:
            hosts.append(arguments.master)
        if arguments.workers:
            hosts = hosts + Parameter.expand(arguments.workers)

        if hosts is None:
            Console.error("You need to specify at least one master or worker")
            return ""

        if arguments.setup:

            self.run_script(name="hadoop.setup", hosts=hosts)

        elif arguments.start:

            self.run_script(name="hadoop.start", hosts=hosts)

        elif arguments.stop:

            self.run_script(name="hadoop.stop", hosts=hosts)

        elif arguments.test:

            self.run_script(name="hadoop.test", hosts=hosts)

        elif arguments.check:

            self.run_script(name="hadoop.check", hosts=hosts)

    def __init__(self, master=None, workers=None):
        """

        :param master:
        :param workers:
        """
        self.master = master
        self.workers = workers
        self.script = Script()
        self.service = "hadoop"
        self.scripts()

    def run(self,
            script=None,
            hosts=None,
            username=None,
            processors=4,
            verbose=False):

        results = []

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

        hostname = os.uname()[1]
        for command in script.splitlines():
            print (hosts, "->", command)
            if command.startswith("#") or command.strip() == "":
                pass
                # print (command)
            elif len(hosts) == 1 and hosts[0] == hostname:
                os.system(command)
            elif len(hosts) == 1 and hosts[0] != hostname:
                host = hosts[0]
                os.system(f"ssh {host} {command}")
            else:
                result = Host.ssh(hosts=hosts,
                                  command=command,
                                  username=username,
                                  key="~/.ssh/id_rsa.pub",
                                  processors=processors,
                                  executor=os.system)
                results.append(result)
        if verbose:
            pprint(results)
            for result in results:
                print(Printer.write(result, order=['host', 'stdout']))
        return results

    def scripts(self):

        version = "3.2.0"

        self.script["hadoop.check"] = """
            hostname
            uname -a
        """

        self.script["hadoop.test"] = """
            rm -rf $HADOOP_HOME/hadoopdata/hdfs/datanode
            rm -rf $HADOOP_HOME/hadoopdata/hdfs/namenode
            echo "Y" | hdfs namenode -format
            $HADOOP_HOME/sbin/start-dfs.sh
            $HADOOP_HOME/sbin/start-yarn.sh
            hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.0.jar pi 2 5
            $HADOOP_HOME/sbin/stop-all.sh
        """

        # install on master: java -> jps -> hadoop
        self.script["hadoop.setup"] = """
            echo "Y" | sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/setup-master.sh
            cd ~
            wget https://archive.apache.org/dist/hadoop/common/hadoop-3.2.0/hadoop-3.2.0.tar.gz
            sudo tar -xvzf hadoop-3.2.0.tar.gz -C /opt/
            sudo mv /opt/hadoop-3.2.0 /opt/hadoop
            sudo chown pi:pi -R /opt/hadoop
            sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/master-bashrc-env.sh
            sh ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/install-hadoop-master2.sh
        """

        self.script["hadoop.start"] = """
            rm -rf $HADOOP_HOME/hadoopdata/hdfs/datanode
            rm -rf $HADOOP_HOME/hadoopdata/hdfs/namenode
            echo "Y" | hdfs namenode -format
            $HADOOP_HOME/sbin/start-dfs.sh
            $HADOOP_HOME/sbin/start-yarn.sh
        """

        self.script["hadoop.stop"] = """
            $HADOOP_HOME/sbin/stop-all.sh
        """

        # self.script["spark.setup.worker"] = """
        #     sudo apt-get update
        #     sudo apt-get install default-jdk
        #     sudo apt-get install scala
        #     cd ~
        #     sudo tar -xzf sparkout.tgz
        #     sudo cp ~/.bashrc ~/.bashrc-backup
        # """
        #

        # for the line below, you havents send "worker-installation.sh" to
        # workers.
        self.script["copy.hadoop.to.worker"] = """
            cd /usr/lib/jvm/java-8-openjdk-armhf
            sudo tar -czf openjdkpkg.tgz *
            scp -r /usr/lib/jvm/java-8-openjdk-armhf/openjdkpkg.tgz {user}@{worker}:
        """

        # self.script["spark.uninstall2.4.5"] = """
        #     sudo apt-get remove openjdk-11-jre
        #     sudo apt-get remove scala
        #     cd ~
        #     sudo rm -rf spark-2.4.5-bin-hadoop2.7
        #     sudo rm -f sparkout.tgz
        #     sudo cp ~/.bashrc-backup ~/.bashrc
        # """

        return self.script

    def run_script(self, name=None, hosts=None):
        banner(name)
        results = self.run(script=self.script[name], hosts=hosts, verbose=True)

    def setup(self, arguments):
        """

        :return:
        """
        #
        # SETUP MASTER
        #
        if self.master:
            self.run_script(name="hadoop.setup", hosts=self.master)
            # self.update_bashrc(self)  -?? Do I need this? Might have created
            # bash twice
            self.hadoop_env(self)
            # self.run_script(name="source bashrc ", hosts=self.master) -
            # might need a line to do "source bashrc"
    #
    #     #
    #     # SETUP WORKER
    #     #
    #     if self.workers:
    #         create_spark.setup.worker(self)
    #         create_spark-bashrc.txt(self)
    #         self.run_script(name="copy.hadoop.to.worker", hosts=self.workers)
    #         update_slaves(self)
    #
    #     raise NotImplementedError
    #     # Setup the master with the Spark applications
    #     # hadoop_setup(self)
    #
    #     # Update the master's ~/.bashrc file
    #     # update_bashrc(self)
    #
    #     # Update the master's spark-env.sh file
    #     # hadoop_env(self)
    #
    #     # Create a shell file to run on worker
    #     # create_hadoop.setup.worker(self)
    #
    #     # Create a file that will append to ~/.bashrc on worker
    #     # create_hadoop-bashrc.txt(self)
    #
    #     # Copy Spark shell and bashrc change files to workers, execute shell file on worker
    #     # copy.hadoop.to.worker(self)
    #
    #     # Update slaves file on master
    #     # update_slaves(self)

    def test(self):
        if self.master:
            self.run_script(name="hadoop.test", hosts=self.master)
        raise NotImplementedError

    def update_slaves(self):
        """
        Add new worker name to bottom of slaves file on master
        :return:
        """
        banner("Updating $SPARK_HOME/conf/slaves file")
        script = textwrap.dedent("""
           {user}@{worker}
        """)
        Installer.add_script("$SPARK_HOME/conf/slaves", script)

    def update_bashrc(self):
        """
        Add the following lines to the bottom of the ~/.bashrc file
        :return:
        """
        banner("Updating ~/.bashrc file")
        script = textwrap.dedent("""
                export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf
                export HADOOP_HOME=/opt/hadoop
                # export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
                export PATH=/home/pi/ENV3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games:/opt/hadoop/bin:/opt/hadoop/sbin:
           """)
        Installer.add_script("~/.bashrc", script)

    def hadoop_env(self, filename="/opt/hadoop/etc/hadoop/hadoop-env.sh"):
        # set up hadoop env file
        name = "Hadoop"
        banner(name)
        script = textwrap.dedent("""
            export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))
        """)
        Installer.add_script(filename, script)

    # @staticmethod
    # def create_hadoop_setup_worker():
    #     """
    #     This file is created on master and copied to worker, then executed from master
    #     :return:
    #     """
    #
    #
    #     banner("Creating the hadoop.setup.worker.sh file")
    #     version = "3.2.0"
    #     script = textwrap.dedent("""
    #                 #!/usr/bin/env bash
    #                 sudo apt-get update
    #                 sudo apt-get install default-jdk
    #                 sudo apt-get install scala
    #                 cd ~
    #                 sudo tar -xzf sparkout.tgz
    #                 cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
    #                 sudo cp ~/.bashrc ~/.bashrc-backup
    #                 sudo cp ~/temp-bashrc ~/.bashrc
    #                 sudo rm ~/temp-bashrc
    #                 sudo chmod 777 ~/spark-{version}-bin-hadoop2.7/
    #           """)
    #
    #
    #     f = open("~/spark-setup-worker.sh", "x")
    #     f.write("~/spark-setup-worker.sh has been created")
    #     f.close()
    #     Installer.add_script("~/spark-setup-worker.sh", script)


    # def create_hadoop-bashrc.txt(self):
    #     """
    #     Test to add at bottome of ~/.bashrc.  File is created on master and copied to worker
    #     :return:
    #     """
    #     script = textwrap.dedent("""
    #                     # ################################################
    #                     # SPARK BEGIN
    #                     #
    #                     #JAVA_HOME
    #                     export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
    #                     #SCALA_HOME
    #                     export SCALA_HOME=/usr/share/scala
    #                     export PATH=$PATH:$SCALA_HOME/bin
    #                     #SPARK_HOME
    #                     export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
    #                     export PATH=$PATH:$SPARK_HOME/bin
    #                     #
    #                     # SPARK END
    #                     # ################################################
    #               """)
    #
    #     f = open("~/spark-bashrc.txt", "x")
    #     f.write("~/spark-bashrc.txt has been created")
    #     f.close()
    #     Installer.add_script("~/spark-bashrc.txt", script)

    def ssh_add(self):
        # test if this works from within python
        os.system("eval $(ssh-agent)")
        os.system("ssh-add")

 #   def install(self):
 #       raise NotImplementedError