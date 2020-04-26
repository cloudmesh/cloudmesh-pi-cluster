#!/usr/bin/env bash
sudo apt-get install openjdk-8-jre
sudo apt-get install scala
cd ~
sudo wget http://apache.osuosl.org/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz -O sparkout2-3-4.tgz
sudo tar -xzf sparkout2-3-4.tgz
cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
sudo cp ~/.bashrc ~/.bashrc-backup
sudo cp ~/temp-bashrc ~/.bashrc
sudo rm ~/temp-bashrc
