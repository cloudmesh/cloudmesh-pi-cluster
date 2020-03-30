import textwrap
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import os
from cloudmesh.cluster.Installer import Installer
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

        if arguments.setup:

            raise NotImplementedError

        elif arguments.start:

            self.start(master=self.master)

        elif arguments.stop:

            self.stop(master=self.master)

        elif arguments.test:

            self.test(master=self.master)

        elif arguments.check:

            hosts = []
            if arguments.master:
                hosts.append(arguments.master)
            if arguments.workers:
                hosts = hosts + Parameter.expand(arguments.workers)

            if hosts is None:
                Console.error("You need to specify at least one master or worker")
                return ""

            pprint(hosts)
            self.check(hosts=hosts)


    def __init__(self, master=None, workers=None):
        """

        :param master:
        :param workers:
        """
        self.master = master
        self.workers = workers

    def run(self, script=None, hosts=None, username=None, processors=4):

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
        return results

    def check(self, hosts=None):
        banner("Spark setup")
        script = textwrap.dedent("""
             # ################################################
             # BEGIN TEST SETUP
             #
             
             hostname
             uname -a
             ls 
             
             # 
             # END TEST SETUP
             # ################################################
         """)
        results = self.run(script=script, hosts=hosts)
        pprint(results)
        for result in results:
            print(Printer.write(result, order=['host', 'stdout']))

    def setup(self):
        """

        :return:
        """
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

    def spark_setup(self, hosts):
        banner("Spark setup")
        script = textwrap.dedent("""
            # ################################################
            # SPARK SETUP
            #
            sudo apt-get install openjdk-8-jre
            sudo apt-get install scala
            cd /usr/local/spark
            sudo wget http://apache.osuosl.org/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz -O sparkout2-3-4.tgz
            sudo tar -xzf sparkout2-3-4.tgz
        """)
        self.run(script=script, hosts=hosts)

    #
    # Bug: this is not yet done on the hosts.
    # why not create it locally and scp ....
    #
    def spark_env(self, filename="/usr/local/spark/spark/conf/spark-env.sh"):
        #
        # should hthis also not be in bashrc?
        #
        script = textwrap.dedent("""
            #JAVA_HOME
            export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
        """)
        # Q: IS THSI ADDED OR OVERWRITE?
        Installer.add_script(filename, script)

    def spark_setup_master(self, master=None):
        script = textwrap.dedent("""
            cd /usr/share/scala-2.11
            sudo tar -cvzf scalaout2-11.tar.gz *
            cd /usr/lib/jvm/java-8-openjdk-armhf
            sudo tar -cvzf javaout8.tgz *
            cd /usr/local/spark/spark
            sudo tar -cvzf sparkout.2-3-4.tgz *
        """)
        self.run(script=script, host=master)

    def copy_files_to_workers(self, user="pi", workers=None):
        script = textwrap.dedent("""
            scp -r $SCALA_HOME/scalaout2-11.tar.gz {user}@{worker}:
            scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz {user}@{worker}:
            scp -r /usr/local/spark/spark/sparkout.2-3-4.tgz {user}@{worker}:
            scp -r ~/spark-setup-worker.sh {user}@{worker}:
        """)
        self.run(script=script, hosts=workers)

    def setup_worker(self, workers=None):
        script = textwrap.dedent("""
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
        """)
        self.run(script=script, hosts=workers)

    def create_slaves_file_in_master(self, workers=None):
        """
        Within the Master's spark directory and conf folder is a slaves file
        indicating the slaves

        :param workers:
        :return:
        """
        filename = "/usr/local/spark/spark/conf/slaves"

        content = readfile(filename)
        content += "localhost" + "\n" # should the master be a slave?
        for worker in workers:
            content += worker +"\n"
        writefile(filename)

    def start(self, master=None):
        script = textwrap.dedent("""
            $SPARK_HOME/sbin/start-master.sh
            $SPARK_HOME/sbin/start-slaves.sh
        """)
        self.run(script=script, hosts=master)

    def test(self, master=None):
        script = textwrap.dedent("""
            cd /usr/local/spark/spark/bin 
            $ run-example SparkPi 4 10
        """)
        self.run(script=script, hosts=master)

    def stop(self, master=None):
        script = textwrap.dedent("""
            $SPARK_HOME/sbin/stop-master.sh
            $SPARK_HOME/sbin/stop-slaves.sh
        """)
        self.run(script=script, hosts=master)

    def ssh_add(self):
        # test if this works from within python
        os.system("eval $(ssh-agent)")
        os.system("ssh-add")

