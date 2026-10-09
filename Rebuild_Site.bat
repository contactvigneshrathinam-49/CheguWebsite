@echo off
setlocal
:: CheGu Website — Rebuild Site
cd /d "%~dp0Website"

echo ============================================
echo  CheGu Website — Rebuild Site
echo ============================================
echo.

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

echo Generating website HTML pages...
"%PY_CMD%" generate_pages.py
if errorlevel 1 (
    echo ERROR: generate_pages.py failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Done! Site rebuilt successfully.
echo ============================================
echo.
pause
endlocal
