import textwrap
import os

class Spark:

    def setup(self):
        #Setup the master with the Spark applications
        master_code_setup(self)
        #Update the master's ~/.bashrc file
        update_bashrc(self)
        #Update the master's spark-env.sh file
        update_spark-env(self)
        #Copy Spark files to workers
        copy_spark_to_worker(self)
        #Run setup on workers
        setup_spark_workers(self)

    def master_code_setup(self):
        os.system(sudo apt-get install openjdk-8-jre)
        os.system(sudo apt-get install scala)
        os.system(sudo mkdir /usr/local/spark)
        os.system(cd /usr/local/spark)
        os.system(sudo wget http://apache.osuosl.org/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz -O sparkout2-3-4.tgz)
        os.system(sudo tar -xzf sparkout2-3-4.tgz)
        #raise NotImplementedError

    def update_bashrc(self):
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
    def spark-env(self):
        script = textwrap.dedent("""
        #JAVA_HOME
        export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
        """)

    def copy_spark_to_worker(self):
        raise NotImplementedError

    def setup_spark_workers(self):
        raise NotImplementedError
