# Production startup script for Finance SMS Logger (Windows)
# This script sets up and runs the application in production mode with Waitress

Write-Host "🚀 Starting Finance SMS Logger in Production Mode" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install/upgrade dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "credentials" | Out-Null

# Check environment variables
Write-Host "🔧 Checking environment configuration..." -ForegroundColor Yellow
python -c @"
import os
from config import get_env_variable
try:
    api_key = get_env_variable('API_KEY')
    if not api_key:
        print('⚠️  API_KEY not set')
    else:
        print('✅ API_KEY configured')
        
    gsheet_id = get_env_variable('GSHEET_SHARED_WORKBOOK_ID')
    if not gsheet_id or gsheet_id == 'your-shared-workbook-id-here':
        print('⚠️  GSHEET_SHARED_WORKBOOK_ID not configured')
    else:
        print('✅ Google Sheets workbook configured')
        
    # Check Google credentials
    google_vars = ['GOOGLE_PROJECT_ID', 'GOOGLE_CLIENT_EMAIL', 'GOOGLE_PRIVATE_KEY']
    missing_google = [var for var in google_vars if not get_env_variable(var)]
    if missing_google:
        print(f'⚠️  Missing Google credentials: {missing_google}')
    else:
        print('✅ Google credentials configured')
        
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Configuration check failed" -ForegroundColor Red
    exit 1
}

Write-Host "🌐 Starting Waitress server..." -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Run with Waitress using the production script
python production.py --mode performance
