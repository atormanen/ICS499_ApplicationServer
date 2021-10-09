#!/bin/bash
systemctl stop jar_app.service
git stash
git fetch
git pull
mkdir -p ./logs
touch ./logs/app_server.log
chmod +x -R *
systemctl restart jar_app.service
tail -n 100 -f ./logs/app_server.log
