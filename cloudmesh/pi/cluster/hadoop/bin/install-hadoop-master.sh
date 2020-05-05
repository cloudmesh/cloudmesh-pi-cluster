#! /usr/bin/env bash

cd ~
wget https://archive.apache.org/dist/hadoop/common/hadoop-3.2.0/hadoop-3.2.0.tar.gz
sudo tar -xvzf hadoop-3.2.0.tar.gz -C /opt/
sudo mv /opt/hadoop-3.2.0 /opt/hadoop
sudo chown pi:pi -R /opt/hadoop
sh ~/sp20-516-252/pi_hadoop/bin/master-bashrc-env.sh