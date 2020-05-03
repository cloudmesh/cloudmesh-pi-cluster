#! /bin/sh

echo
echo "Install Spark"
echo
cd ~
sudo wget http://mirror.metrocast.net/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz -O sparkout.tgz
sudo tar -xzf sparkout.tgz