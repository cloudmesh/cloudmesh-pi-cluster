#!/usr/bin/env bash
scp -r /usr/share/scala/scalaout2-11.tar.gz pi@green001:
scp -r /usr/lib/jvm/java-8-openjdk-armhf/javaout8.tgz pi@green001:
scp -r /spark-2.3.4-bin-hadoop2.7/sparkout.2-3-4.tgz pi@green001:
scp -r /bin/spark-setup-worker.sh pi@green001:
scp -r /bin/spark-env.sh.setup.sh pi@green001:
scp -r /bin/spark-bashrc.sh pi@green001: