#!/usr/bin/env bash
#sudo apt-get install openjdk-8-jre
sudo apt-get update
sudo apt-get install default-jdk
sudo apt-get install scala
cd ~
sudo wget http://mirror.metrocast.net/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz -O sparkout.tgz
sudo tar -xzf sparkout.tgz
cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
sudo cp ~/.bashrc ~/.bashrc-backup
sudo cp ~/temp-bashrc ~/.bashrc
sudo rm ~/temp-bashrc
sudo chmod 777 ~/spark-2.4.5-bin-hadoop2.7/
sudo cp /home/pi/spark-2.4.5-bin-hadoop2.7/conf/slaves.template /home/pi/spark-2.4.5-bin-hadoop2.7/conf/slaves

