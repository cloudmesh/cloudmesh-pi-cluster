#!/usr/bin/env bash
sudo apt-get remove openjdk-8-jre
sudo apt-get remove scala
cd ~
sudo rm -rf spark-2.3.4-bin-hadoop2.7
sudo rm -f sparkout2-3-4.tgz
sudo cp ~/.bashrc-backup ~/.bashrc