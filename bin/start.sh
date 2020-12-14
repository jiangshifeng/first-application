#!/bin/bash
#app_name=$1
app_name='first-application'
source /tmp/$app_name/app_conf
WORK_PATH=$(cd `dirname $0`;pwd)
cd $WORK_PATH
cd ..
python run.py $app_port
#nohup python run.py >> $app_log &
