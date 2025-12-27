# 🚀 Quick Start - Running the Litigation System

## Single Command Launch

The easiest way to run the Private AI Litigation Knowledge System is using one of the provided launcher scripts.

### Windows

**Option 1: Double-click**
- Double-click `run.bat`

**Option 2: Command Prompt**
```bash
run.bat
```

**Option 3: PowerShell**
```powershell
.\run.ps1
```

### Linux/Mac

**Make executable (first time only):**
```bash
chmod +x run.sh
```

**Run:**
```bash
./run.sh
```

## What the Scripts Do

The launcher scripts automatically:

1. ✅ **Check Python installation** - Verifies Python 3.8+ is installed
2. ✅ **Create virtual environment** - Creates `.venv` if it doesn't exist
3. ✅ **Activate virtual environment** - Activates the venv automatically
4. ✅ **Install dependencies** - Installs required packages from `litigation_requirements.txt`
5. ✅ **Verify files** - Checks all required Python files are present
6. ✅ **Launch application** - Starts the Gradio server

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment
```bash
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

### 2. Activate Virtual Environment
```bash
# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r litigation_requirements.txt
```

### 4. Run Application
```bash
python main.py
```

## Accessing the Application

Once running, open your browser and navigate to:
- **http://localhost:7860** or
- **http://127.0.0.1:7860**

## Troubleshooting

### "Python is not installed"
- Install Python 3.8+ from https://www.python.org/
- Make sure Python is added to your PATH

### "Failed to create virtual environment"
- Make sure you have write permissions in the current directory
- Try running as administrator (Windows) or with sudo (Linux/Mac)

### "Failed to install dependencies"
- Check your internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`
- Some packages may require additional system libraries

### "Module not found" errors
- Make sure you activated the virtual environment
- Reinstall dependencies: `pip install -r litigation_requirements.txt`

## Virtual Environment Benefits

Using venv (virtual environment) provides:
- ✅ **Isolated dependencies** - Won't conflict with other Python projects
- ✅ **Clean environment** - Only installs what's needed
- ✅ **Easy cleanup** - Just delete `.venv` folder to remove everything
- ✅ **Reproducible** - Same environment every time

## Files Created

The launcher will create:
- `.venv/` - Virtual environment directory (can be deleted and recreated)
- `uploaded_documents/` - Your uploaded files (created on first upload)
- `knowledge_base/` - Search index and metadata (created on first use)

## Stopping the Application

Press `Ctrl+C` in the terminal to stop the server.

