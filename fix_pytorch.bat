@echo off
REM Fix PyTorch DLL Error on Windows
REM This script will reinstall PyTorch with Windows-compatible CPU-only version

echo ============================================================
echo   Fixing PyTorch DLL Error
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run run.bat first to create the virtual environment
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [INFO] Uninstalling problematic PyTorch packages...
pip uninstall -y torch torchvision torchaudio sentence-transformers transformers >nul 2>&1

echo.
echo [INFO] Installing Windows-compatible PyTorch (CPU-only)...
echo This may take a few minutes...

REM Install PyTorch CPU-only version for Windows (most stable)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

if errorlevel 1 (
    echo [ERROR] Failed to install PyTorch
    echo Trying alternative installation method...
    
    REM Alternative: Install from PyPI (may be slower but more compatible)
    pip install torch torchvision torchaudio --no-cache-dir
)

if errorlevel 1 (
    echo [ERROR] Failed to install PyTorch with alternative method
    pause
    exit /b 1
)

echo.
echo [INFO] Reinstalling sentence-transformers...
pip install sentence-transformers --no-cache-dir

if errorlevel 1 (
    echo [ERROR] Failed to reinstall sentence-transformers
    pause
    exit /b 1
)

echo.
echo [INFO] Verifying installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print('PyTorch loaded successfully!')"

if errorlevel 1 (
    echo.
    echo [ERROR] PyTorch still not working. You may need to:
    echo 1. Install Visual C++ Redistributables from Microsoft
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo 2. Restart your computer after installing
    echo 3. Try running this script again
    echo.
) else (
    echo.
    echo [OK] PyTorch installation fixed successfully!
    echo.
    echo You can now run the application with:
    echo   python main.py
    echo.
)

pause

