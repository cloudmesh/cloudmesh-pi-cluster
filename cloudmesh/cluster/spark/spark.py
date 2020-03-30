import textwrap
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import os
from cloudmesh.cluster.Installer import Installer
from cloudmesh.cluster.Installer import Script
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Host import Host
from pprint import pprint


# see also: https://github.com/cloudmesh-community/sp20-516-246/tree/master/pi_spark


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

        version = "2.3.4"

        self.script["spark.check"] = """
            hostname
            uname -a
        """

        self.script["spark.test"] = """
            cd /usr/local/spark/spark/bin 
            run-example SparkPi 4 10
        """

        self.script["spark.setup"] = """
            sudo apt-get install openjdk-8-jre
            sudo apt-get install scala
            cd /usr/local/spark
            sudo wget http://apache.osuosl.org/spark/spark-{version}/spark-{version}-bin-hadoop2.7.tgz -O sparkout-{version}.tgz
            sudo tar -xzf sparkout-{version}.tgz
        """

        self.script["spark.master.setup"] = """
            cd /usr/share/scala-2.11
            sudo tar -cvzf scalaout2-11.tar.gz *
            cd /usr/lib/jvm/java-8-openjdk-armhf
            sudo tar -cvzf javaout8.tgz *
            cd /usr/local/spark/spark
            sudo tar -cvzf sparkout-{version}.tgz *
        """

        self.script["spark.master.copy"] = """
            scp -r $SCALA_HOME/scalaout2-11.tar.gz {user}@{worker}:
            scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz {user}@{worker}:
            scp -r /usr/local/spark/spark/sparkout-{version}.tgz {user}@{worker}:
            scp -r ~/spark-setup-worker.sh {user}@{worker}:
        """

        self.script["spark.worker.setup"] = """
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
            sudo mv ~/sparkout-{version}.tgz /usr/local/spark/spark/
            cd /usr/local/spark/spark
            sudo tar -xvzf sparkout-{version}.tgz
        """

        self.script[f"spark.master.copy"] = """
            scp -r $SCALA_HOME/scalaout2-11.tar.gz {user}@{worker}:.
            scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz {user}@{worker}:.
            scp -r /usr/local/spark/spark/sparkout-{version}.tgz {user}@{worker}:.
            scp -r ~/spark-setup-worker.sh {user}@{worker}:.
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
            self.run_script(name="spark.master.setup", hosts=self.master)

        #
        # SETUP WORKER
        #
        if self.workers:
            self.run_script(name="spark.master.copy", hosts=self.workers)
            self.run_script(name="spark.worker.setup", hosts=self.workers)

        raise NotImplementedError
        # Setup the master with the Spark applications
        # master_code_setup(self)

        # Update the master's ~/.bashrc file
        # update_bashrc(self)

        # Update the master's spark-env.sh file
        # update_spark-env(self)

        # Copy Spark files to workers
        #copy_spark_to_worker(self)

        # Run setup on workers
        # setup_spark_workers(self)

    #
    # Bug: this is not yet done on the hosts.
    # why not create it locally and scp ....
    #
    def update_bashrc(self):
        """

        :return:
        """
        script = textwrap.dedent("""
        
            # ################################################
            # SPARK BEGIN
            #
            
            # SCALA_HOME
            export SCALA_HOME=/usr/share/scala
            export PATH=$PATH:$SCALA_HOME/bin
            
            # SPARK_HOME
            export SPARK_HOME=/usr/local/spark/spark
            export PATH=$PATH:$SPARK_HOME/bin
            
            #
            # SPARK END
            # ################################################
            
        """)
        Installer.add_script("~/.bashrc", script)

    #
    # Bug: this is not yet done on the hosts.
    # why not create it locally and scp ....
    #
    def spark_env(self, filename="/usr/local/spark/spark/conf/spark-env.sh"):
        #
        # should hthis also not be in bashrc?
        #
        name = "spack."
        banner(name)
        script = textwrap.dedent("""
            #JAVA_HOME
            export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
        """)
        # Q: IS THSI ADDED OR OVERWRITE?
        Installer.add_script(filename, script)



    def ssh_add(self):
        # test if this works from within python
        os.system("eval $(ssh-agent)")
        os.system("ssh-add")

