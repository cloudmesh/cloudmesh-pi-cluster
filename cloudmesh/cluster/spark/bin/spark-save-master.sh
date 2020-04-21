#!/usr/bin/env bash
cd /usr/share/scala-2.11
sudo tar -cvzf scalaout2-11.tar.gz *
cd /usr/lib/jvm/java-8-openjdk-armhf
sudo tar -cvzf javaout8.tgz *
cd /usr/local/spark/spark
sudo tar -cvzf sparkout.2-3-4.tgz *