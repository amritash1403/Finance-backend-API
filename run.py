#!/usr/bin/env python
"""
Run script for the Finance SMS Logger Flask Application.
"""

import os
import sys
import dotenv
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

dotenv.load_dotenv(project_dir / ".env")

# Check if virtual environment is activated
if not hasattr(sys, "real_prefix") and not (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
):
    print("WARNING: Virtual environment not activated!")
    print("Please activate it with: .\\venv\\Scripts\\activate.ps1")
    print()

# Check if Google credentials exist
credentials_file = project_dir / "credentials" / "google-credentials.json"
if not credentials_file.exists():
    print("ERROR: Google credentials not found!")
    print(f"Please create the file: {credentials_file}")
    print("Copy from: credentials/google-credentials.json.example")
    print()

# Import and run the Flask app
try:
    from app import app, AppConfig

    print("Finance SMS Logger Flask Application")
    print("=" * 50)
    print(f"Debug mode: {AppConfig.DEBUG}")
    print(f"API Prefix: {AppConfig.API_PREFIX}")
    print(f"Log Level: {AppConfig.LOG_LEVEL}")
    print("=" * 50)
    print("Starting server...")
    print("Available endpoints:")
    print("  GET  /health")
    print("  POST /api/v1/log")
    print("  POST /api/v1/test-parser")
    print("  GET  /api/v1/sheets/{month-year}")
    print("=" * 50)

    # Create necessary directories
    os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)

except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Please ensure all dependencies are installed: pip install -r requirements.txt"
    )
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
