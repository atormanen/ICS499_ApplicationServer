#!/bin/bash
cd /var/jar_app_server/ICS499_ApplicationServer/ || return 1
/usr/bin/python3 controller.py &
