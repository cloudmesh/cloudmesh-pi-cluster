#! /usr/bin/env bash

cat >> ~/.bashrc << EOF
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
# export PATH=/home/pi/ENV3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games:/opt/hadoop/bin:/opt/hadoop/sbin:
EOF
