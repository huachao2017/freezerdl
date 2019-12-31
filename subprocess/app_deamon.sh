#!/bin/bash
today=`date +"%Y-%m-%d"`
ps -ef | grep app_deamon_process | grep -v grep | awk '{print $2}' | xargs kill -9
nohup python3 -u /data/src/freezerdl/freezers/subprocess/app_deamon_process.py >> /data/src/freezerdl/logs/app_deamon_process.log""$today 2>&1 &
