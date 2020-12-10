#!/bin/bash
app_name='first-application'
app_log="/var/log/$app_name.log"
WORK_PATH=$(cd `dirname $0`;pwd)
cd $WORK_PATH
cd ..
python run.py
#nohup python run.py >> $app_log &
