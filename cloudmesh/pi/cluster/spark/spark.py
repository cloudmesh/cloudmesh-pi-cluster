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
        self.version = "2.4.5"
        self.user = "pi"
        self.script = Script()
        self.service = "spark"
        #self.port = 6443
        self.hostname = os.uname()[1]
        self.scripts()

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
        master = arguments.master
        workers = Parameter.expand(arguments.workers)


        hosts = []
        if arguments.master:
            hosts.append(arguments.master)
        if arguments.workers:
            hosts = hosts + Parameter.expand(arguments.workers)

        #hosts = None
        master = None
        if arguments.master:
            master = arguments.master


        #hosts = None
        if arguments.workers:
            hosts = Parameter.expand(arguments.workers)

        if hosts is None:
            Console.error("You need to specify at least one master or worker")
            return ""

        if arguments.setup:

            #  pi hadoop setup [--master=MASTER] [--workers=WORKERS]

            self.setup(master, workers)
            #self.run_script(name="sparksetup", hosts=hosts)

        elif arguments.start:

            self.start(master)

        elif arguments.stop:

            self.stop(master)

        elif arguments.test:

            self.test(master)

        elif arguments.check:

            self.check(master, hosts)

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

        self.script["sparksetup"] = """
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

        return self.script

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

    def setup(self, master= None, hosts=None):
        # Setup master
        if master is None and hosts:
            Console.error("You must specify a master to set up nodes")
            return ""

        # Setup Spark on the master
        if hosts is None:
            if master is not None:

                if type(master) != list:
                    master = Parameter.expand(master)
                #
                # TODO - bug I should be able to run this even if I am not on master
                #
                banner(f"Setup Master: {master[0]}")
                self.run_script(name="sparksetup", hosts=self.master)
                #os.system("sudo apt-get update")
                print(Spark.update_bashrc())

        # Setup workers and update master's slaves file
        #
        #
        if hosts is not None:
            if master is not None:
                banner(f"Get files from {master[0]}")
                print(self.create_spark_setup_worker())
                print(self.create_spark_bashrc_txt())
                self.run_script(name="copy.spark.to.worker", hosts=self.master)
                print(self.update_slaves())

        # Print created cluster
        #self.view()

        # raise NotImplementedError

    def start(self, master=None, hosts=None):
        # Setup master
        if master is None and hosts:
            Console.error("You must specify a master to start cluster")
            raise ValueError

        # Setup Spark on the master
        if master is not None:

            if type(master) != list:
                master = Parameter.expand(master)
            #
            # TODO - bug I should be able to run this even if I am not on master
            #
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
        # Stop Spark
        if master is None and hosts:
            Console.error("You must specify a master to stop cluster")
            raise ValueError

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

    def update_slaves(self):
        """
        Add new worker name to bottom of slaves file on master
        :return:
        """
        banner("Updating $SPARK_HOME/conf/slaves file")
        script = textwrap.dedent("""
           {user}@{worker}
        """)
        if not self.dryrun:
            Installer.add_script("$SPARK_HOME/conf/slaves", script)

    def update_bashrc(self):
        """
        Add the following lines to the bottom of the ~/.bashrc file
        :return:
        """
        banner("Updating ~/.bashrc file")
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
        # Q: IS THIS ADDED OR OVERWRITE?
        Installer.add_script(filename, script)

    def create_spark_setup_worker(self):
        """
        This file is created on master and copied to worker, then executed on worker from master
        :return:
        """
        banner("Creating the spark.setup.worker.sh file")
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
        version = "2.4.5"
        java_version = "11"
        script = textwrap.dedent("""
                        # ################################################
                        # SPARK BEGIN
                        #
                        #JAVA_HOME
                        export JAVA_HOME=/usr/lib/jvm/java-{java_version}-openjdk-armhf/
                        #SCALA_HOME
                        export SCALA_HOME=/usr/share/scala
                        export PATH=$PATH:$SCALA_HOME/bin
                        #SPARK_HOME
                        export SPARK_HOME=~/spark-{version}-bin-hadoop2.7
                        export PATH=$PATH:$SPARK_HOME/bin
                        #
                        # SPARK END
                        # ################################################
                  """)

        if self.dryrun:
            print (script)
        else:
            f = open("/home/pi/spark-bashrc.txt", "w+")
            #f.write("test")
            f.close()
            Installer.add_script("~/spark-bashrc.txt", script)
