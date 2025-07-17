#!/usr/bin/env python
"""
WSGI entry point for production deployment.
This file is used by Gunicorn and other WSGI servers.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import the Flask application
from app import app

# Create necessary directories on startup
try:
    from config import AppConfig

    os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create logs directory: {e}")

# WSGI application object
application = app

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    app.run(host="0.0.0.0", port=5000)
