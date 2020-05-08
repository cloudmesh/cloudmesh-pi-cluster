#!/usr/bin/env bash
echo "Y" | sudo apt-get remove openjdk-11-jre
echo "Y" | sudo apt-get remove scala
cd ~
sudo rm -rf spark*
sudo cp ~/.bashrc-backup ~/.bashrc