# Private AI Litigation Knowledge System - PowerShell Launcher
# This script will check dependencies and launch the application

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Private AI Litigation Knowledge System" -ForegroundColor Cyan
Write-Host "  PowerShell Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed (try python first, then python3)
$pythonCmd = $null
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "python"
        Write-Host "[OK] Python found" -ForegroundColor Green
        Write-Host $pythonVersion
    }
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "python3"
            Write-Host "[OK] Python3 found" -ForegroundColor Green
            Write-Host $pythonVersion
        }
    } catch {
        Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please do one of the following:" -ForegroundColor Yellow
        Write-Host "1. Install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
        Write-Host "2. Add Python to your PATH environment variable" -ForegroundColor Yellow
        Write-Host "3. Use the full path to python.exe" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To check if Python is installed, try:" -ForegroundColor Yellow
        Write-Host "  Get-Command python" -ForegroundColor Yellow
        Write-Host "  Get-Command python3" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Could not find Python" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists, create if not
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "[INFO] No virtual environment found" -ForegroundColor Yellow
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
    Write-Host "[INFO] Upgrading pip..." -ForegroundColor Yellow
    & $pythonCmd -m pip install --upgrade pip
}

# Check if dependencies are installed
Write-Host ""
Write-Host "[INFO] Checking dependencies..." -ForegroundColor Yellow
$gradioInstalled = pip show gradio 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing required packages..." -ForegroundColor Yellow
    pip install -r litigation_requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[OK] Dependencies already installed" -ForegroundColor Green
}

# Check if required files exist
$requiredFiles = @(
    "litigation_system.py",
    "document_processor.py",
    "knowledge_base.py",
    "ai_analyzer.py"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[ERROR] $file not found" -ForegroundColor Red
        Write-Host "Please make sure you're in the correct directory" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "[OK] All required files found" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting Application..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Run the application
& $pythonCmd litigation_system.py

# Check exit status
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Application exited with an error" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

