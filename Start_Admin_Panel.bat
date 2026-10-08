@echo off
echo Starting CheGu Local Admin Panel...
cd /d "%~dp0Website"
python -m pip install flask werkzeug Pillow
python admin_server.py
pause
