#!/bin/bash
# CheGu Website — Add Photos & Publish (Mac)
# Double-click this file from Finder to open the Publisher App.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 &>/dev/null; then
    osascript -e 'display alert "Python 3 Not Found" message "Please install Python 3 from https://www.python.org/downloads/"'
    exit 1
fi

python3 Add_Photos_And_Publish.py
