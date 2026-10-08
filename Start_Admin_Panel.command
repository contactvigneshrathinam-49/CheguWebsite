#!/bin/bash
cd "$(dirname "$0")/Website"
echo "Starting CheGu Local Admin Panel..."
python3 -m pip install flask werkzeug
python3 admin_server.py
