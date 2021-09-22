#!/bin/bash
git stash
git fetch
git pull
chmod +x -R *
systemctl restart jar_app.service
