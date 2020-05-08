#!/usr/bin/env bash
sudo apt-get remove openjdk-11-jre
sudo apt-get remove scala
cd ~
sudo rm -rf spark*
sudo cp ~/.bashrc-backup ~/.bashrc