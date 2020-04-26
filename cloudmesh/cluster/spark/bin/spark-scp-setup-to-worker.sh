#!/usr/bin/env bash
scp /bin/spark-setup.sh pi@green001:
scp ~/spark-bashrc.txt pi@green001:
ssh pi@green001 sh ~/spark-setup.sh