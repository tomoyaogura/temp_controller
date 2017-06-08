#!/bin/bash
sleep 10
cd /
cd /home/pi/temp_controller
nohup python web.py &
nohup python run.py &
cd /
