#!/bin/bash
# CheGu Website — Connect Chegu's GitHub (One-Time Setup for Mac)
cd "$(dirname "$0")"

echo "========================================================"
echo "  CHEGU WEBSITE — ONE-TIME GITHUB CONNECT SETUP"
echo "========================================================"
echo ""
echo "This connects this folder to Chegu's own GitHub account"
echo "so the 1-click Publish button works automatically."
echo ""

read -p "Enter Chegu's GitHub Repo URL (e.g. https://github.com/chegu/website.git): " GITHUB_REPO
if [ -z "$GITHUB_REPO" ]; then
    echo "No URL entered. Exiting."
    exit 1
fi

read -p "Enter Chegu's Name / Username: " GITHUB_USER
read -p "Enter Chegu's Email: " GITHUB_EMAIL

git remote set-url origin "$GITHUB_REPO"
[ -n "$GITHUB_USER" ] && git config user.name "$GITHUB_USER"
[ -n "$GITHUB_EMAIL" ] && git config user.email "$GITHUB_EMAIL"
git config credential.helper osxkeychain

echo ""
echo "========================================================"
echo "  Connecting and testing push to your repository..."
echo "========================================================"
echo "(If a browser opens asking for GitHub login, approve it)"
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] SUCCESS! Connected to your GitHub."
    echo "     Now you can just double-click 'Add_Photos_And_Publish' whenever you want!"
else
    echo ""
    echo "[!] Push failed or cancelled. You can also sign in via GitHub Desktop."
fi

echo ""
read -p "Press Enter to close..."
