@echo off
setlocal

echo ============================================
echo  CheGu Website — Rebuild Site
echo ============================================
echo.

REM Change to the Website folder (relative to this script's location)
cd /d "%~dp0Website"

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

REM Install required Python packages if missing
echo Checking Python packages...
python -m pip install Pillow --quiet --disable-pip-version-check

echo.
echo Step 1: Optimizing images from pORTFOLIO...
echo (This may take a moment if new photos were added)
python optimize_images.py
if errorlevel 1 (
    echo ERROR: optimize_images.py failed. See error above.
    pause
    exit /b 1
)

echo.
echo Step 2: Rebuilding all HTML pages...
python generate_pages.py
if errorlevel 1 (
    echo ERROR: generate_pages.py failed. See error above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Done! Site rebuilt successfully.
echo ============================================
echo.
echo Next steps:
echo  1. Open GitHub Desktop
echo  2. Review the changes
echo  3. Write a short commit message (e.g. "Added new photos")
echo  4. Click Commit to main
echo  5. Click Push origin
echo  6. Netlify will auto-deploy in about 1 minute.
echo.
pause
endlocal
