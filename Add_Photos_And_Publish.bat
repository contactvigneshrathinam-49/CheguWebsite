@echo off
:: CheGu Website — Add Photos & Publish (Windows)
:: Double-click this file to open the Publisher App.

cd /d "%~dp0"
python Add_Photos_And_Publish.py
if errorlevel 1 (
    echo Python not found. Please install Python from https://www.python.org/
    pause
)
