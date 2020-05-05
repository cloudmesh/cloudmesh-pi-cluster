#!/usr/bin/env bash

cd /usr/lib/jvm/java-8-openjdk-armhf
# zip all the files
sudo tar -czf openjdkpkg.tgz *
# send over to worker node red001
scp -r /usr/lib/jvm/java-8-openjdk-armhf/openjdkpkg.tgz red001:
# scp -r /usr/lib/jvm/java-8-openjdk-armhf/openjdkpkg.tgz red002: