#!/usr/bin/env bash
#   note:  #!/bin/bash is what's known as a shebang or a hashbang. #! are special characters
#   that tell the kernel "this file should be run by feeding it to the following program".
#   (You'll also commonly see this written as #!/usr/bin/env bash,
#   which is sometimes considered a more portable way to invoke an interpreter.)
cat >> ~/.bashrc << EOF
#SCALA_HOME
export SCALA_HOME=/usr/share/scala
export PATH=$PATH:$SCALA_HOME/bin
#SPARK_HOME
export SPARK_HOME=/spark-2.3.4-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin
EOF
