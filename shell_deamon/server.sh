#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
ps -ef | grep "manage.py runserver" | grep -v grep | awk '{print $2}' | xargs kill -9
nohup python3 -u /home/src/freezerdl/manage.py runserver 0.0.0.0:80 >> /home/src/freezerdl/logs/server.log""$today 2>&1 &
