import textwrap
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import os

# see also: https://github.com/cloudmesh-community/sp20-516-246/tree/master/pi_spark


class Spark:

    def run(self, script):
        for line in script:
            if line.startswith("#"):
                print (line)
            else:
                os.system(line)


    def install(self):
        raise NotImplementedError

    def upate_bashrc(self):
        banner("Update bashrc")
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

    def spark_setup(self):
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
        self.run(script)

    def spark_env(self, filename="/usr/local/spark/spark/conf/spark-env.sh"):
        #
        # should hthis also not be in bashrc?
        #
        script = textwrap.dedent("""
            #JAVA_HOME
            export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
        """)
        self.run(script)

    def spark_setup_master(self):
        script = textwrap.dedent("""
            cd /usr/share/scala-2.11
            sudo tar -cvzf scalaout2-11.tar.gz *
            cd /usr/lib/jvm/java-8-openjdk-armhf
            sudo tar -cvzf javaout8.tgz *
            cd /usr/local/spark/spark
            sudo tar -cvzf sparkout.2-3-4.tgz *
        """)
        self.run(script)

    def copy_files_to_workerss(self, workers):
        script = textwrap.dedent("""
            scp -r $SCALA_HOME/scalaout2-11.tar.gz pi@yellow-002:
            scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz pi@yellow-002:
            scp -r /usr/local/spark/spark/sparkout.2-3-4.tgz pi@yellow-002:
            scp -r ~/spark-setup-worker.sh pi@yellow-002:
        """)
        self.run(script)

    def setup_worker(self):
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
        self.run(script)

    def create_slaves_file_in_master(self, workers):
        """
        Within the Master's spark directory and conf folder is a slaves file
        indicating the slaves

        :param workerss:
        :return:
        """
        filename = "/usr/local/spark/spark/conf/slaves"

        content = readfile(filename)
        content += "localhost" + "\n" # should the master be a slave?
        for worker in workers:
            content += worker +"\n"
        writefile(filename)

    def start(self):
        script = textwrap.dedent("""
            $SPARK_HOME/sbin/start-master.sh
            $SPARK_HOME/sbin/start-slaves.sh
        """)
        self.run(script)

    def test(self):
        script = textwrap.dedent("""
            cd /usr/local/spark/spark/bin 
            $ run-example SparkPi 4 10
        """)
        self.run(script)

    def stop(self):
        script = textwrap.dedent("""
            $SPARK_HOME/sbin/stop-master.sh
            $SPARK_HOME/sbin/stop-slaves.sh
        """)
        self.run(script)

    def ssh_add(self):
        # test if this works from within python
        os.system("eval $(ssh-agent)")
        os.system("ssh-add")
