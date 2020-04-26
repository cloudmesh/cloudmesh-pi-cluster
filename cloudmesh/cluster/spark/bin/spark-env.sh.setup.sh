#!/usr/bin/env bash
sudo cp /spark-2.3.4-bin-hadoop2.7/conf/spark-env.sh.template /spark-2.3.4-bin-hadoop2.7/conf/spark-env.sh
cat >> /spark-2.3.4-bin-hadoop2.7/conf/spark-env.sh << EOF
#JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
EOF