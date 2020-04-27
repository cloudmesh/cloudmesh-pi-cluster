#!/usr/bin/env bash
scp ~/spark-bashrc.txt pi@green001:
scp /bin/spark-uninstall2.4.5.sh pi@green001:
scp /bin/spark-setup-worker.sh pi@green001:
scp ~/sparkout.tgz pi@green001:
ssh pi@green001 sh ~/spark-setup-worker.sh
sudo cat >> $SPARK_HOME/conf/slaves << EOF
pi@green001
EOF