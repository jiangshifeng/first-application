#!/bin/bash
#app_port='8811'
#app_name=$1
app_name='first-application'
source /tmp/$app_name/app_conf
app_pid=`lsof -i:$app_port|grep LISTEN|tail -1|awk '{print $2}'`
if [ -z $app_pid ];then
    echo "应用未启动"
    exit 0
else
    kill -9 $app_pid > /dev/null 2>&1
    if [ $? -eq 0 ];then
    #    echo "应用关闭成功"
        exit 0
    else
    #    echo "应用关闭失败"
        exit 1
    fi
fi
