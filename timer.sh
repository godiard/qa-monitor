#!/bin/sh
if [ -n "$(ps ax | grep qa-monitor.py | grep -v grep)" ]; then 
    echo "FOUND QA-MONIOR RUNNING. EXIT"
    exit
fi
cd /home/qamonitor/qa-monitor
git pull
python qa-monitor.py
