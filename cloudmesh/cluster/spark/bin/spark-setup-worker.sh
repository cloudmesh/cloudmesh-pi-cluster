#!/usr/bin/env bash
sudo apt-get install openjdk-8-jre
sudo apt-get install scala
cd ~
sudo tar -xzf sparkout.tgz
cat ~/.bashrc ~/spark-bashrc.txt > ~/temp-bashrc
sudo cp ~/.bashrc ~/.bashrc-backup
sudo cp ~/temp-bashrc ~/.bashrc
sudo rm ~/temp-bashrc
sudo chmod 777 ~/spark-2.4.5-bin-hadoop2.7/