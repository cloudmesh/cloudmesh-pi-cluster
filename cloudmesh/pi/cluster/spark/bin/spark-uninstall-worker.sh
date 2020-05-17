#!/usr/bin/env bash
echo "Y" | sudo apt autoremove openjdk-11*
echo "Y" | sudo apt autoremove openjdk-8*
echo "Y" | sudo apt-get remove scala
cd ~
sudo rm -rf spark*
sudo cp ~/.bashrc-backup ~/.bashrc