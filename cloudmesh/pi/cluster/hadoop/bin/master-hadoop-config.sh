#! /usr/bin/env bash

cp ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/hadoop-config-file/core-site.xml /opt/hadoop/etc/hadoop/core-site.xml
cp ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/hadoop-config-file/hdfs-site.xml /opt/hadoop/etc/hadoop/hdfs-site.xml
cp ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/hadoop-config-file/mapred-site.xml /opt/hadoop/etc/hadoop/mapred-site.xml
cp ~/cm/cloudmesh-pi-cluster/cloudmesh/pi/cluster/hadoop/bin/hadoop-config-file/yarn-site.xml /opt/hadoop/etc/hadoop/yarn-site.xml
hdfs namenode -format
