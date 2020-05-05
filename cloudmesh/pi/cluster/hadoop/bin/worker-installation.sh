#! /usr/bin/env bash

# create java directory
sudo mkdir /opt/jdk
sudo mv ~/openjdkpkg.tgz /opt/jdk/
sudo tar -zxf /opt/jdk/openjdkpkg.tgz -C /opt/jdk

# check if files are there
ls /opt/jdk

#update alternatives so the command java point to the new jdk
sudo update-alternatives --install /usr/bin/java java /opt/jdk/jre/bin/java 100
sudo update-alternatives --install /usr/bin/javac javac /opt/jdk/jre/bin/java 100

#check if java command is pointing to " link currently points to /opt/jdk/jdk1.8.0_05/bin/java"
update-alternatives --display java

#check if java command is pointing to " link currently points to /opt/jdk/jdk1.8.0_05/bin/javac"
update-alternatives --display javac

#check if java is running
java -version