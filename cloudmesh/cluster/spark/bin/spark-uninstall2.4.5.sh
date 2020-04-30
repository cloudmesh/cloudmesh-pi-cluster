#!/usr/bin/env bash
sudo apt-get remove openjdk-11-jre
sudo apt-get remove scala
cd ~
sudo rm -rf spark-2.4.5-bin-hadoop2.7
sudo rm -f sparkout.tgz
sudo cp ~/.bashrc-backup ~/.bashrc