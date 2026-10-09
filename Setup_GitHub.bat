@echo off
:: CheGu Website — Connect Chegu's GitHub (One-Time Setup)
cd /d "%~dp0"
echo ========================================================
echo   CHEGU WEBSITE — ONE-TIME GITHUB CONNECT SETUP
echo ========================================================
echo.
echo This connects this folder to Chegu's own GitHub account
echo so the 1-click Publish button works automatically.
echo.

set /p GITHUB_REPO="Enter Chegu's GitHub Repo URL (e.g. https://github.com/chegu/website.git): "
if "%GITHUB_REPO%"=="" (
    echo No URL entered. Exiting.
    pause
    exit /b
)

set /p GITHUB_USER="Enter Chegu's Name / Username: "
set /p GITHUB_EMAIL="Enter Chegu's Email: "

git remote set-url origin %GITHUB_REPO%
if not "%GITHUB_USER%"=="" git config user.name "%GITHUB_USER%"
if not "%GITHUB_EMAIL%"=="" git config user.email "%GITHUB_EMAIL%"
git config credential.helper manager

echo.
echo ========================================================
echo   Connecting and testing push to your repository...
echo ========================================================
echo (If a GitHub sign-in window appears in your browser, click 'Authorize')
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo [!] Could not push automatically.
    echo     Tip: You can also use GitHub Desktop to log in and push.
) else (
    echo.
    echo [OK] SUCCESS! Connected to your GitHub.
    echo      Now you can just double-click 'Add_Photos_And_Publish' whenever you want!
)

echo.
pause
