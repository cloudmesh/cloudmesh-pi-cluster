#!/usr/bin/env bash
cat >> /usr/local/spark/spark/conf/spark-env.sh << EOF
#JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/
EOF