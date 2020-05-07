#!/usr/bin/env bash
cat >> ~/.bashrc << EOF
#JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-armhf/
#SCALA_HOME
export SCALA_HOME=/usr/share/scala
#SPARK_HOME
export SPARK_HOME=~/spark-2.4.5-bin-hadoop2.7
export PATH=/home/pi/ENV3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$SPARK_HOME/bin:$SCALA_HOME/bin
EOF