@echo off
:: CheGu Website — CheGu Portfolio Studio (Windows)
cd /d "%~dp0"

set "PY_CMD=python"
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=py"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    )
)

"%PY_CMD%" Add_Photos_And_Publish.py
if errorlevel 1 (
    echo.
    echo [!] Could not run CheGu Studio.
    echo Please make sure Python is installed.
    pause
)
