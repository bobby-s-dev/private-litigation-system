@echo off
REM Private AI Litigation Knowledge System - Windows Launcher
REM This script will check dependencies and launch the application

echo ============================================================
echo   Private AI Litigation Knowledge System
echo   Windows Launcher
echo ============================================================
echo.

REM Check if Python is installed (try python first, then python3)
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH
        echo.
        echo Please do one of the following:
        echo 1. Install Python 3.8+ from https://www.python.org/
        echo 2. Add Python to your PATH environment variable
        echo 3. Use the full path to python.exe
        echo.
        echo To check if Python is installed, try:
        echo   where python
        echo   where python3
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
        echo [OK] Python3 found
        python3 --version
    )
) else (
    set PYTHON_CMD=python
    echo [OK] Python found
    python --version
)

REM Check if virtual environment exists, create if not
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo [INFO] Upgrading pip...
    %PYTHON_CMD% -m pip install --upgrade pip
)

REM Check if dependencies are installed
echo.
echo [INFO] Checking dependencies...
pip show gradio >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    pip install -r litigation_requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

REM Check if required files exist
if not exist "litigation_system.py" (
    echo [ERROR] litigation_system.py not found
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

if not exist "document_processor.py" (
    echo [ERROR] document_processor.py not found
    pause
    exit /b 1
)

if not exist "knowledge_base.py" (
    echo [ERROR] knowledge_base.py not found
    pause
    exit /b 1
)

if not exist "ai_analyzer.py" (
    echo [ERROR] ai_analyzer.py not found
    pause
    exit /b 1
)

echo.
echo [OK] All required files found
echo.
echo ============================================================
echo   Starting Application...
echo ============================================================
echo.

REM Run the application
%PYTHON_CMD% litigation_system.py

REM If the application exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error
    pause
)

