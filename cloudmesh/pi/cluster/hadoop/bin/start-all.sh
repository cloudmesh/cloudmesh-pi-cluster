#!/usr/bin/env bash

cd ~/.ssh
cat id_rsa.pub >> authorized_keys
cd $HADOOP_HOME/sbin/
./start-all.sh