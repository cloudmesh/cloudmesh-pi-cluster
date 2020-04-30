import os
import textwrap
from pprint import pprint

from cloudmesh.cluster.Installer import Installer
from cloudmesh.cluster.Installer import Script
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner

# see also: https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/cluster/spark

class Spark:

    def execute(self, arguments):
        """
        pi spark setup --master=MASTER --workers=WORKER
        pi spark start --master=MASTER --workers=WORKER
        pi spark stop --master=MASTER --workers=WORKER
        pi spark test --master=MASTER --workers=WORKER

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

            self.run_script(name="spark.setup", hosts=hosts)

        elif arguments.start:

            self.run_script(name="spark.start", hosts=hosts)

        elif arguments.stop:

            self.run_script(name="spark.stop", hosts=hosts)

        elif arguments.test:

            self.run_script(name="spark.test", hosts=hosts)

        elif arguments.check:

            self.run_script(name="spark.check", hosts=hosts)

    def __init__(self, master=None, workers=None):
        """

        :param master:
        :param workers:
        """
        self.master = master
        self.workers = workers
        self.script = Script()
        self.service = "spark"
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

        version = "2.4.5"

        self.script["spark.check"] = """
            hostname
            uname -a
        """

        self.script["spark.test"] = """
            sh $SPARK_HOME/sbin/start-all.sh
            $SPARK_HOME/bin/run-example SparkPi 4 10
            sh $SPARK_HOME/sbin/stop-all.sh
        """

        self.script["spark.setup"] = """
            sudo apt-get update
            sudo apt-get install default-jdk
            sudo apt-get install scala
            cd ~
            sudo wget http://mirror.metrocast.net/apache/spark/spark-{version}/spark-{version}-bin-hadoop2.7.tgz -O sparkout.tgz
            sudo tar -xzf sparkout.tgz
            sudo cp ~/.bashrc ~/.bashrc-backup
            sudo chmod 777 ~/spark-{version}-bin-hadoop2.7/conf
            sudo cp /home/pi/spark-{version}-bin-hadoop2.7/conf/slaves.template /home/pi/spark-{version}-bin-hadoop2.7/conf/slaves
        """

        self.script["spark.setup.worker"] = """
            sudo apt-get update
            sudo apt-get install default-jdk
            sudo apt-get install scala
            cd ~
            sudo tar -xzf sparkout.tgz
            sudo cp ~/.bashrc ~/.bashrc-backup
        """

        self.script["copy.spark.to.worker"] = """
            scp /bin/spark-setup-worker.sh {user}@{worker}:
            scp ~/sparkout.tgz {user}@{worker}:
            ssh {user}@{worker} sh ~/spark-setup-worker.sh
        """

        self.script["spark.uninstall2.4.5"] = """
            sudo apt-get remove openjdk-11-jre
            sudo apt-get remove scala
            cd ~
            sudo rm -rf spark-2.4.5-bin-hadoop2.7
            sudo rm -f sparkout.tgz
            sudo cp ~/.bashrc-backup ~/.bashrc
        """

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
            self.run_script(name="spark.setup", hosts=self.master)
            update_bashrc(self)

        #
        # SETUP WORKER
        #
        if self.workers:
            create_spark.setup.worker(self)
            create_spark-bashrc.txt(self)
            self.run_script(name="copy.spark.to.worker", hosts=self.workers)
            update_slaves(self)

        raise NotImplementedError
        # Setup the master with the Spark applications
        # spark_setup(self)

        # Update the master's ~/.bashrc file
        # update_bashrc(self)

        # Update the master's spark-env.sh file
        # update_spark-env(self)

        # Copy Spark files to workers
        #copy-spark-to-worker(self)

        # Run setup on workers
        # setup_spark_workers(self)

        # Update slaves file on master

    def test(self):
        if self.master:
            self.run_script(name="spark.test", hosts=self.master)
        raise NotImplementedError

    def update_slaves(self):
        """
        Add new worker name to bottom of slaves file on master
        :return:
        """
        script = textwrap.dedent("""
           {user}@{worker}
        """)
        Installer.add_script("$SPARK_HOME/conf/slaves", script)

    def update_bashrc(self):
        """
        Add the following lines to the bottom of the ~/.bashrc file
        :return:
        """
        script = textwrap.dedent("""

               # ################################################
               # SPARK BEGIN
               #
               #JAVA_HOME
               export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
               #SCALA_HOME
               export SCALA_HOME=/usr/share/scala
               export PATH=$PATH:$SCALA_HOME/bin
               #SPARK_HOME
               export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
               export PATH=$PATH:$SPARK_HOME/bin
               #
               # SPARK END
               # ################################################

           """)
        Installer.add_script("~/.bashrc", script)

    def spark_env(self, filename="$SPARK_HOME/conf/spark-env.sh"):
        #
        # This is extra and probably not needed as also set in ~/.bashrc
        #
        name = "spark."
        banner(name)
        script = textwrap.dedent("""
            #JAVA_HOME
            export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
        """)
        # Q: IS THSI ADDED OR OVERWRITE?
        Installer.add_script(filename, script)

    def create_spark.setup.worker(self):
        """
        This file is created on master and copied to worker, then executed from master
        :return:
        """
        version = "2.4.5"
        script = textwrap.dedent("""
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
                    sudo chmod 777 ~/spark-{version}-bin-hadoop2.7/
              """)


        f = open("~/spark-setup-worker.sh", "x")
        f.write("~/spark-setup-worker.sh has been created")
        f.close()
        Installer.add_script("~/spark-setup-worker.sh", script)


    def create_spark-bashrc.txt(self):
        """
        Test to add at bottome of ~/.bashrc.  File is created on master and copied to worker
        :return:
        """
        script = textwrap.dedent("""
                        # ################################################
                        # SPARK BEGIN
                        #
                        #JAVA_HOME
                        export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
                        #SCALA_HOME
                        export SCALA_HOME=/usr/share/scala
                        export PATH=$PATH:$SCALA_HOME/bin
                        #SPARK_HOME
                        export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
                        export PATH=$PATH:$SPARK_HOME/bin
                        #
                        # SPARK END
                        # ################################################
                  """)

        f = open("~/spark-bashrc.txt", "x")
        f.write("~/spark-bashrc.txt has been created")
        f.close()
        Installer.add_script("~/spark-bashrc.txt", script)

    def ssh_add(self):
        # test if this works from within python
        os.system("eval $(ssh-agent)")
        os.system("ssh-add")

