#! /usr/bin/env bash

cat >> /opt/hadoop/etc/hadoop/hadoop-env.sh << EOF
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))
EOF