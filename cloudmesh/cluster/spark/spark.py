import textwrap

class Spark:

    def install(self):
        raise NotImplementedError

    def upate_bashrc(self):
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

