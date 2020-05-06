import os
import textwrap
from pprint import pprint

#import cloudmesh.pi.cluster
from cloudmesh.pi.cluster.Installer import Installer
from cloudmesh.pi.cluster.Installer import Script
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner

# see also: https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/master/cloudmesh/cluster/spark

class Spark(Installer):

    def __init__(self, master=None, workers=None):
        """
        :param master:
        :param workers:
        """
        self.master = master
        self.workers = workers
        self.java_version = "11"
        self.version = "2.4.5"
        self.user = "pi"
        self.script = Script()
        self.service = "spark"
        #self.port = 6443
        self.hostname = os.uname()[1]
        self.scripts()

    def scripts(self):

        self.script["spark.check"] = """
               hostname
               uname -a
           """

        self.script["spark.test"] = """
               sh $SPARK_HOME/sbin/start-all.sh
               $SPARK_HOME/bin/run-example SparkPi 4 10
               sh $SPARK_HOME/sbin/stop-all.sh
           """

        self.script["spark.setup.master"] = """
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
               scp /bin/spark-setup-worker.sh {user}@self.workers:
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

        self.script["update.bashrc"] = """

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

           """

        script["spark.setup.worker.sh"] = """
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
              """

        return self.script

    def execute(self, arguments):
        """
        pi spark setup --master=MASTER --workers=WORKER
        pi spark start --master=MASTER --workers=WORKER
        pi spark stop --master=MASTER --workers=WORKER
        pi spark test --master=MASTER --workers=WORKER
        pi spark check --master=MASTER --worker=WORKER

        :param arguments:
        :return:
        """
        self.dryrun = arguments["--dryrun"]
        master = Parameter.expand(arguments.master)
        workers = Parameter.expand(arguments.workers)

        if len(master) > 1:
            Console.error("You can have only one master")
        master = master[0]
        # find master and worker from arguments

        if arguments.master:
            hosts.append(arguments.master)

        if arguments.workers:
            hosts = Parameter.expand(arguments.workers)

        if workers is not None and master is None:
            Console.error("You need to specify at least one master or worker")
            return ""

        # do the action on master amd workers found
        if arguments.setup:
            self.setup(master, workers)
        elif arguments.start:
            self.start(master, workers)
        elif arguments.stop:
            self.stop(master, workers)
        elif arguments.test:
            self.test(master, workers)
        elif arguments.check:
            self.check(master, workers)


    def run(self,
            script=None,
            hosts=None,
            username=None,
            processors=4,
            verbose=False):

        results = []

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

        for command in script.splitlines():
            if hosts == None:
                hosts = ""
            if command.startswith("#") or command.strip() == "":
                print(command)
            elif len(hosts) == 1 and hosts[0] == self.hostname:
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


    def run_script(self, name=None, hosts=None):
        banner(name)
        print("self.script = ")
        pprint(self.script)

        results = self.run(script=self.script[name], hosts=hosts, verbose=True)

    def setup(self, master= None, workers=None):

        #
        # SETUP THE MASTER
        #
        banner(f"Setup Master: {master}")
        self.run_script(name="sparksetup", hosts=self.master)
        #os.system("sudo apt-get update")

        if "SPARK_HOME" not in os.environ:
            Console.error("$SPARK_HOME is not set")
            return ""

        spark_home = os.environ("SPARK_HOME")
        filename =  "{spark_home}/conf/slaves"
        banner(f"Updating file: {filename}")
        filename =
        if not self.dryrun:
            Installer.add_script(fileanme, "{user}@{worker}")

        banner(f"Setup bashrc: {master}")
        print(Spark.update_bashrc())

        #
        # SETUP THE WORKER. STEP 1: GET THE FILES FROM MASTER
        #
        banner(f"Get files from {master}")
        print(self.create_spark_setup_worker())
        self.run_script(name="copy.spark.to.worker", hosts=self.workers)

        #
        # SETUP THE WORKER. SETUP BASHRC ON WORKERS
        #

        print(self.create_spark_bashrc_txt())

        print(self.update_slaves())

        # Print created cluster
        #self.view()

        # raise NotImplementedError

    def start(self, master=None, hosts=None):

        # Setup Spark on the master

        if master is not None:

            if type(master) != list:
                master = Parameter.expand(master)

            banner(f"Start Master: {master[0]}")
            os.system("sh $SPARK_HOME/sbin/start-all.sh")
            # command = Installer.oneline(f"""
            #           sh $SPARK_HOME/sbin/start-all.sh -
            #           """)

        # raise NotImplementedError

    def test(self, master=None, hosts=None):
        banner(f"Listing $SPARK_HOME from {master[0]}")
        os.system("ls $SPARK_HOME")
        os.system("$SPARK_HOME/bin/run-example SparkPi 4 10")

    def stop(self, master=None, hosts=None):

        # Stop Spark on master and all workers
        if master is not None:

            if type(master) != list:
                master = Parameter.expand(master)
            #
            # TODO - bug I should be able to run this even if I am not on master
            #
            banner(f"Start Master: {master[0]}")
            os.system("sh $SPARK_HOME/sbin/stop-all.sh")
            #command = Installer.oneline(f"""
            #           sh $SPARK_HOME/sbin/stop-all.sh -
            #           """)

        # raise NotImplementedError


    def update_bashrc(self):
        """
        Add the following lines to the bottom of the ~/.bashrc file
        :return:
        """
        banner("Updating ~/.bashrc file")
        script = textwrap.dedent(self.script["update.bashrc"])
        Installer.add_script("~/.bashrc", script)

    def create_spark_setup_worker(self):
        """
        This file is created on master and copied to worker, then executed on worker from master
        :return:
        """
        banner("Creating the spark.setup.worker.sh file")
        script = self.script["spark.setup.worker.sh"]

        if self.dryrun:
            print (script)
        else:
            f = open("/home/pi/spark-setup-worker.sh", "w+")
            #f.write("test")
            f.close()
            Installer.add_script("~/spark-setup-worker.sh", script)

    def create_spark_bashrc_txt(self):
        """
        Test to add at bottome of ~/.bashrc.  File is created on master and copied to worker
        :return:
        """
        script = self.script["update.bashrc"]

        if self.dryrun:
            print (script)
        else:
            f = open("/home/pi/spark-bashrc.txt", "w+")
            #f.write("test")
            f.close()
            Installer.add_script("~/spark-bashrc.txt", script)
