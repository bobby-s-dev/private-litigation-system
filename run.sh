#!/bin/bash
# Private AI Litigation Knowledge System - Linux/Mac Launcher
# This script will check dependencies and launch the application

echo "============================================================"
echo "  Private AI Litigation Knowledge System"
echo "  Linux/Mac Launcher"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found"
python3 --version

# Check if virtual environment exists, create if not
if [ -d ".venv" ]; then
    echo "[OK] Virtual environment found"
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "[INFO] No virtual environment found"
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "[INFO] Upgrading pip..."
    python -m pip install --upgrade pip
fi

# Check if dependencies are installed
echo ""
echo "[INFO] Checking dependencies..."
if ! pip show gradio &> /dev/null; then
    echo "[INFO] Installing required packages..."
    pip install -r litigation_requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
    echo "[OK] Dependencies installed"
else
    echo "[OK] Dependencies already installed"
fi

# Check if required files exist
if [ ! -f "litigation_system.py" ]; then
    echo "[ERROR] litigation_system.py not found"
    echo "Please make sure you're in the correct directory"
    exit 1
fi

if [ ! -f "document_processor.py" ]; then
    echo "[ERROR] document_processor.py not found"
    exit 1
fi

if [ ! -f "knowledge_base.py" ]; then
    echo "[ERROR] knowledge_base.py not found"
    exit 1
fi

if [ ! -f "ai_analyzer.py" ]; then
    echo "[ERROR] ai_analyzer.py not found"
    exit 1
fi

echo ""
echo "[OK] All required files found"
echo ""
echo "============================================================"
echo "  Starting Application..."
echo "============================================================"
echo ""

# Run the application
python3 litigation_system.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application exited with an error"
    exit 1
fi

