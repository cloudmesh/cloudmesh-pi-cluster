#!/usr/bin/env bash
sh $SPARK_HOME/sbin/start-master.sh
sh $SPARK_HOME/sbin/start-slaves.sh
#Test program:
$SPARK_HOME/bin/run-example SparkPi 4 10
sh $SPARK_HOME/sbin/stop-all.sh