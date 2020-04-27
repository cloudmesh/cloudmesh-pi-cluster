#!/usr/bin/env bash
scp ~/spark-bashrc.txt pi@green001:
scp /bin/spark-uninstall.sh pi@green001:
scp ~/sparkout.tgz pi@green001:
ssh pi@green001 sh ~/spark-worker-setup.sh
cat >> $SPARK_HOME/conf/slaves << EOF
pi@green001
EOF