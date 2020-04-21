#!/usr/bin/env bash
scp -r $SCALA_HOME/scalaout2-11.tar.gz pi@yellow-001:
scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz pi@yellow-001:
scp -r /usr/local/spark/spark/sparkout.2-3-4.tgz pi@yellow-001:
scp -r ~/spark-setup-worker.sh pi@yellow-001:
scp -r ~/spark-env.sh.setup.sh pi@yellow-001:
scp -r ~/spark-bashrc.sh pi@yellow-001: