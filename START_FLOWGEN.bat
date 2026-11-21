@echo off
title FlowGen Image Studio v1.0
cd /d "%~dp0"

echo ===================================================================
echo   FLOWGEN IMAGE STUDIO v1.0
echo   Unlimited Image Generation API Bridge
echo   Built by Ali Bhatti (@alirash3ed)
echo ===================================================================
echo.

set "PY_EXE="
if exist "browser2api\.venv\Scripts\python.exe" (
    set "PY_EXE=browser2api\.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PY_EXE=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_EXE=python"
    )
)

if "%PY_EXE%"=="" (
    echo [ERROR] Python environment not found!
    echo Please ensure Python and the virtual environment in browser2api\.venv are installed.
    echo.
    pause
    exit /b 1
)

set "SCRIPT_PATH="
if exist "browser2api\run_hud.py" (
    set "SCRIPT_PATH=browser2api\run_hud.py"
) else if exist "run_hud.py" (
    set "SCRIPT_PATH=run_hud.py"
) else (
    echo [ERROR] run_hud.py not found!
    echo.
    pause
    exit /b 1
)

echo [*] Python environment detected: %PY_EXE%
echo [*] Starting FlowGen Studio at http://127.0.0.1:8787 ...
echo [*] Opening your default web browser automatically...
echo [*] (Keep this terminal open while using FlowGen. Press Ctrl+C to stop.)
echo.

"%PY_EXE%" "%SCRIPT_PATH%" %*

if %errorlevel% neq 0 (
    echo.
    echo [!] Studio stopped with exit code: %errorlevel%
    pause
)
