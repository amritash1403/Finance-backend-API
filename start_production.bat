@echo off
REM Production startup script for Finance SMS Logger (Windows Batch)
REM This script sets up and runs the application in production mode with Waitress

echo 🚀 Starting Finance SMS Logger in Production Mode
echo =================================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found. Please run setup first.
    exit /b 1
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "logs\" mkdir logs
if not exist "credentials\" mkdir credentials

REM Check environment configuration
echo 🔧 Checking environment configuration...
python -c "import os; from config import get_env_variable; print('✅ Configuration check passed' if get_env_variable('API_KEY') else '⚠️ API_KEY not configured')"

if errorlevel 1 (
    echo ❌ Configuration check failed
    exit /b 1
)

echo 🌐 Starting Waitress server...
echo =================================================

REM Run with Waitress using the production script
python production.py --mode performance

pause
