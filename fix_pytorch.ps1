# Fix PyTorch DLL Error on Windows
# This script will reinstall PyTorch with Windows-compatible CPU-only version

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Fixing PyTorch DLL Error" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run run.ps1 first to create the virtual environment" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "[INFO] Uninstalling problematic PyTorch packages..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio sentence-transformers transformers 2>&1 | Out-Null

Write-Host ""
Write-Host "[INFO] Installing Windows-compatible PyTorch (CPU-only)..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow

# Install PyTorch CPU-only version for Windows (most stable)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install PyTorch" -ForegroundColor Red
    Write-Host "Trying alternative installation method..." -ForegroundColor Yellow
    
    # Alternative: Install from PyPI (may be slower but more compatible)
    pip install torch torchvision torchaudio --no-cache-dir
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install PyTorch with alternative method" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Reinstalling sentence-transformers..." -ForegroundColor Yellow
pip install sentence-transformers --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to reinstall sentence-transformers" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Verifying installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print('PyTorch loaded successfully!')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] PyTorch installation fixed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the application with:" -ForegroundColor Yellow
    Write-Host "  python main.py" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] PyTorch still not working. You may need to:" -ForegroundColor Red
    Write-Host "1. Install Visual C++ Redistributables from Microsoft" -ForegroundColor Yellow
    Write-Host "   https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
    Write-Host "2. Restart your computer after installing" -ForegroundColor Yellow
    Write-Host "3. Try running this script again" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"

