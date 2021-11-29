#!/bin/bash
systemctl stop jar_app.service
git stash
git fetch
git pull
mkdir -p ./logs
chown -R jar_user:jar_user ./*
chmod 0554 -R ./*
chmod 0664 ./logs/app_server.log
chmod 0440 ./params.json
touch ./logs/app_server.log
systemctl restart jar_app.service
tail -n 100 -f ./logs/app_server.log
