#!/bin/bash
# CheGu Website — Rebuild Site (Mac)
# Double-click this file from Finder to rebuild the site.

echo "============================================"
echo " CheGu Website — Rebuild Site"
echo "============================================"
echo ""

# Move to the Website directory relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/Website" || { echo "ERROR: Website folder not found."; exit 1; }

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install from https://www.python.org/downloads/"
    exit 1
fi

echo "Checking Python packages..."
python3 -m pip install Pillow --quiet --disable-pip-version-check

echo ""
echo "Step 1: Optimizing images from pORTFOLIO..."
python3 optimize_images.py || { echo "ERROR: optimize_images.py failed."; exit 1; }

echo ""
echo "Step 2: Rebuilding all HTML pages..."
python3 generate_pages.py || { echo "ERROR: generate_pages.py failed."; exit 1; }

echo ""
echo "============================================"
echo " Done! Site rebuilt successfully."
echo "============================================"
echo ""
echo "Next: commit and push via GitHub Desktop or git."
echo ""
read -p "Press Enter to close..."
