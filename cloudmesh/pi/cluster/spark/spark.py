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
from cloudmesh.common.JobSet import JobSet

class Spark:

    def execute(self, arguments):
        """
        pi spark worker add [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark worker remove [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark setup [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark start [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark stop [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark test [--master=MASTER] [--workers=WORKERS] [--dryrun]
        pi spark check [--master=MASTER] [--workers=WORKERS] [--dryrun]

        :param arguments:
        :return:
        """
        self.master = arguments.master
        self.workers = Parameter.expand(arguments.workers)

        master =[]
        hosts = []
        workers_only =[]
        if arguments.master:
            hosts.append(arguments.master)
            master = arguments.master
        if arguments.workers:
            hosts = hosts + Parameter.expand(arguments.workers)
            workers_only = Parameter.expand(arguments.workers)
        if arguments.dryrun:
            self.dryrun = True

        if hosts is None:
            Console.error("You need to specify at least one master or worker")
            return ""

        if arguments.setup:

            self.setup(master,workers_only)

        elif arguments.start:

            self.run_script(name="spark.start", hosts=master)

        elif arguments.stop:

            self.run_script(name="spark.stop", hosts=master)

        elif arguments.test:

            self.test(master)
            #self.run_script(name="spark.test", hosts=self.master)

        elif arguments.check:

            self.run_script(name="spark.check", hosts=hosts)

        elif arguments.uninstall:

            self.uninstall(master, workers_only)

    def __init__(self, master=None, workers=None):
        """

        :param master:
        :param workers:
        """
        self.master = master
        self.workers = workers
        self.dryrun = False
        self.script = Script()
        self.service = "spark"
        self.java_version = "11"
        self.version = "2.4.5"
        self.user = "pi"
        self.hostname = os.uname()[1]
        self.spark_bin = "~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/spark/bin"
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
            if hosts == None:
                hosts = ""
            if command.startswith("#") or command.strip() == "":
                print(command)
            elif len(hosts) == 1 and hosts[0] == self.hostname:
                host = hosts[0]
                command = command.format(user=self.user, version=self.version, host=host, hostname=hostname)
                print(hosts, "->", command)
                if self.dryrun:
                    Console.info(f"Executiong command >{command}<")
                else:
                    os.system(command)
            elif len(hosts) == 1 and hosts[0] != self.hostname:
                host = hosts[0]
                command = command.format(user=self.user, version=self.version, host=host, hostname=hostname)
                print(hosts, "->", command, hosts)
                if self.dryrun:
                    Console.info(f"Executiong command >{command}<")
                else:
                    os.system(f"ssh {host} {command}")
            else:

                #@staticmethod
                #def run(hosts=None,
                #        command=None,
                #        execute=None,
                #        processors=3,
                #        shell=False,
                #        **kwargs):

                if self.dryrun:
                    executor = print
                else:
                    executor = os.system

                result = Host.ssh(hosts=hosts,
                                  command=command,
                                  username=username,
                                  key="~/.ssh/id_rsa.pub",
                                  processors=processors,
                                  executor=executor,
                                  version=self.version, # this was your bug, you did not pass this along
                                  user=self.user  # this was your bug, you did not pass this along
                                  )
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

        self.script["spark.prereqs"] = """
            sudo apt-get update
            echo "Y" | sudo apt-get install default-jdk
            sudo apt-get install scala
            echo "Y" | sudo apt install libatlas3-base libgfortran5
            sudo pip3 install numpy 
        """

        self.script["spark.download.spark"] = """
            cd ~
            sudo wget http://mirror.metrocast.net/apache/spark/spark-{version}/spark-{version}-bin-hadoop2.7.tgz -O sparkout.tgz
        """

        self.script["spark.install"] = """
            cd ~
            sudo tar -xzf sparkout.tgz
         """

        self.script["spark.bashrc.master"] = """
            sudo cp ~/spark-2.4.5-bin-hadoop2.7/conf/slaves ~/spark-2.4.5-bin-hadoop2.7/conf/slaves-backup
            sudo cp ~/spark-2.4.5-bin-hadoop2.7/conf/slaves.template ~/spark-2.4.5-bin-hadoop2.7/conf/slaves
            sudo chmod -R 777 ~/spark-2.4.5-bin-hadoop2.7/conf/
            echo '' >> ~/spark-2.4.5-bin-hadoop2.7/conf/slaves
            sudo cp ~/.bashrc ~/.bashrc-backup
            cat ~/.bashrc /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/spark/bin/spark-bashrc.txt > ~/temp-bashrc
            sudo cp ~/temp-bashrc ~/.bashrc
            sudo rm ~/temp-bashrc
            export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
            export SCALA_HOME=/usr/share/scala
            export PATH=$PATH:$SCALA_HOME/bin
            export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
            export PATH=$PATH:$SPARK_HOME/bin
         """

        self.script["spark.test"] = """
            sh $SPARK_HOME/sbin/start-all.sh
            $SPARK_HOME/bin/run-example SparkPi 4 10
            sh $SPARK_HOME/sbin/stop-all.sh
        """

        self.script["spark.bashrc.additions"] = """
            #JAVA_HOME
            export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
            #SCALA_HOME
            export SCALA_HOME=/usr/share/scala
            export PATH=$PATH:$SCALA_HOME/bin
            #SPARK_HOME
            export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
            export PATH=$PATH:$SPARK_HOME/bin
        """

        self.script["spark.start"] = """
            cat $SPARK_HOME/conf/slaves
            sh $SPARK_HOME/sbin/start-all.sh
        """

        self.script["spark.stop"] = """
            cat $SPARK_HOME/conf/slaves
            sh $SPARK_HOME/sbin/stop-all.sh
        """

        self.script["spark.uninstall.master"] = """
            echo "Y" | sudo apt-get remove openjdk-11-jre
            echo "Y" | sudo apt-get remove scala
            cd ~
            sudo rm -rf spark-2.4.5-bin-hadoop2.7
            sudo rm -f sparkout.tgz
            sudo cp ~/.bashrc-backup ~/.bashrc
            sudo cp $SPARK_HOME/conf/slaves-backup $SPARK_HOME/conf/slaves
        """

        return self.script

    def run_script(self, name=None, hosts=None):
        banner(name)
        results = self.run(script=self.script[name], hosts=hosts, verbose=True)

    def setup(self,master,hosts):
        #
        # SETUP MASTER
        #
        if self.master:
            banner(f"Setting up master {master}")
            self.run_script(name="spark.prereqs", hosts=master)
            self.run_script(name="spark.download.spark", hosts=master)
            self.run_script(name="spark.install", hosts=master)
            self.run_script(name="spark.bashrc.master", hosts=master)
        #
        # SETUP WORKER
        #
        if self.workers:
            # Copy setup files to each worker and execute the shell program in parallel
            workers = ', '.join(hosts)
            banner(f"Setup Workers: {workers}")
            command = "sh ~/spark-setup-worker.sh"
            jobSet = JobSet("spark_worker_install", executor=JobSet.ssh)
            for host in hosts:
                banner(f"Setting up worker {host}")
                command1 = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/spark/bin/spark-setup-worker.sh pi@{host}:"
                print(command1)
                os.system(command1)
                command2 = f"scp ~/sparkout.tgz pi@{host}:"
                print(command2)
                os.system(command2)
                command3 = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/spark/bin/spark-bashrc.txt pi@{host}:"
                print(command3)
                os.system(command3)
                command4 = f"scp /home/pi/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/spark/bin/spark-uninstall-worker.sh pi@{host}:"
                print(command4)
                os.system(command4)
                jobSet.add({"name": host, "host": host, "command": command})
                self.update_slaves(host)
            banner("Updating workers in parallel")
            jobSet.run(parallel=len(hosts))
            #jobSet.Print()
            banner("Spark setup complete")
        return
    #    #raise NotImplementedError
    #
    #     # Setup Pi workflow
    #     # Setup the Pi master with the prerequisite applications
    #       shell script "spark.prereqs"
    #
    #      # Download Spark on the Pi master
    #       shell script "spark.download.spark"
    #
    #      # Install spark on Pi master
    #       shell script "spark.install"
    #
    #      # Update Pi master's ~/.bashrc file and prepare environment for workers
    #       shell script "spark.bashrc.master"
    #
    #     # Setup a Pi worker by copying files from Pi master to Pi worker & executing a shell file on worker
    #
    #     # Update slaves file on master
    #       function update_slaves(self)

    def test(self,master):
        if self.master:
            banner("Master Pi password needed TWICE - for start and stop")
            self.run_script(name="spark.test", hosts=master)
        if self.workers:
            banner("cms pi spark test intended for master only")
        return

    def update_slaves(self,hosts):
        banner("Updating $SPARK_HOME/conf/slaves file")
        command5 = f"echo 'pi@{hosts}' >> ~/spark-2.4.5-bin-hadoop2.7/conf/slaves "
        print(command5)
        os.system(command5)


    def uninstall(self,master,hosts):
        #
        # Uninstall MASTER
        #
        if self.master:
            banner(f"Uninstall Master: {master}")
            self.run_script(name="spark.uninstall.master", hosts=master)
        #
        # Uninstall WORKER(S)
        #
        if self.workers:
            banner(f"Uninstall Workers: {hosts}")
            command7 = "sh ~/spark-uninstall-worker.sh"
            jobSet = JobSet("spark_worker_uninstall", executor=JobSet.ssh)
            for host in hosts:
                jobSet.add({"name": host, "host": host, "command": command7})
            jobSet.run(parallel=len(hosts))
            #jobSet.Print()
            banner("Successfully uninstalled workers")
        return