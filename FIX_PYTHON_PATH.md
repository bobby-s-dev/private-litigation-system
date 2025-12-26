# 🔧 Fixing Python PATH Issues

If you're seeing the error "Python is not installed or not in PATH", here's how to fix it:

## Quick Fixes

### Option 1: Check if Python is Actually Installed

**Windows (Command Prompt):**
```bash
where python
where python3
```

**Windows (PowerShell):**
```powershell
Get-Command python
Get-Command python3
```

**Linux/Mac:**
```bash
which python
which python3
```

If these commands return nothing, Python is not installed or not in PATH.

### Option 2: Install Python

1. Download Python 3.8+ from: https://www.python.org/downloads/
2. **IMPORTANT:** During installation, check the box that says:
   - ✅ **"Add Python to PATH"** (Windows)
   - This automatically adds Python to your system PATH

3. After installation, restart your terminal/command prompt

### Option 3: Add Python to PATH Manually (Windows)

If Python is installed but not in PATH:

1. **Find Python installation:**
   - Usually: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\`
   - Or: `C:\Python3XX\`

2. **Add to PATH:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System variables", find "Path" → Click "Edit"
   - Click "New" and add:
     - `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\`
     - `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts\`
   - Click "OK" on all dialogs
   - **Restart your terminal/command prompt**

### Option 4: Use Full Path (Temporary Fix)

If you know where Python is installed, you can modify the script to use the full path:

**Edit `run.bat`:**
```batch
REM Change this line:
python --version

REM To (example):
"C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe" --version
```

### Option 5: Use Python Launcher (Windows)

Windows includes a Python launcher that might work:

```bash
py --version
py -m venv .venv
py litigation_system.py
```

## Verify Installation

After fixing, verify Python works:

```bash
python --version
# Should show: Python 3.8.x or higher

python -m pip --version
# Should show: pip version
```

## Common Issues

### "python is not recognized"
- Python is not in PATH
- Use Option 2 or 3 above

### "python3 is not recognized" (Windows)
- On Windows, it's usually just `python`, not `python3`
- The script will try both automatically

### "Permission denied" (Linux/Mac)
- You might need to use `python3` instead of `python`
- Or install Python for your user: `brew install python3` (Mac)

## Still Having Issues?

1. **Check Python installation:**
   - Open a new terminal/command prompt
   - Try: `python --version` or `python3 --version`

2. **Check PATH:**
   - Windows: `echo %PATH%`
   - Linux/Mac: `echo $PATH`
   - Look for Python directories in the output

3. **Reinstall Python:**
   - Uninstall current Python
   - Reinstall from python.org
   - **Make sure to check "Add to PATH" during installation**

4. **Use Anaconda/Miniconda:**
   - If you have Anaconda installed, use:
     ```bash
     conda create -n litigation python=3.11
     conda activate litigation
     pip install -r litigation_requirements.txt
     python litigation_system.py
     ```

## Alternative: Use the Python You Have

If you have Python installed but the script can't find it, you can run manually:

1. **Find your Python:**
   ```bash
   # Windows
   dir C:\Python* /s /b
   dir C:\Users\%USERNAME%\AppData\Local\Programs\Python* /s /b
   
   # Or search in File Explorer for python.exe
   ```

2. **Use full path:**
   ```bash
   "C:\path\to\python.exe" -m venv .venv
   .venv\Scripts\activate
   pip install -r litigation_requirements.txt
   python litigation_system.py
   ```

