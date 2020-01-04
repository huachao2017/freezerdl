#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
ps -ef | grep ai_deamon_process | grep -v grep | awk '{print $2}' | xargs kill -9
nohup python3 -u /home/src/freezerdl/shell_deamon/ai_deamon_process.py >> /home/src/freezerdl/logs/ai_deamon_process.log""$today 2>&1 &
