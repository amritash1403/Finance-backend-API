"""
Development setup script for Finance SMS Logger.
Helps with initial setup and testing.
"""

import os
import json
import shutil
from pathlib import Path


def check_setup():
    """Check if setup is complete."""
    print("Finance SMS Logger - Setup Check")
    print("=" * 50)

    # Check virtual environment
    if os.path.exists("venv"):
        print("✓ Virtual environment exists")
    else:
        print("✗ Virtual environment missing")
        print("  Run: python -m venv venv")

    # Check requirements
    if os.path.exists("requirements.txt"):
        print("✓ Requirements file exists")
    else:
        print("✗ Requirements file missing")

    # Check directories
    dirs = ["credentials", "logs"]
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")

    # Check Google credentials
    creds_file = Path("credentials") / "google-credentials.json"
    if creds_file.exists():
        print("✓ Google credentials file exists")
    else:
        print("✗ Google credentials file missing")
        print("  Copy from: credentials/google-credentials.json.example")

    # Check SMS parser
    if os.path.exists("sms_parser"):
        print("✓ SMS parser module exists")
    else:
        print("✗ SMS parser module missing")

    print("\n" + "=" * 50)
    print("Setup Status Summary:")

    if creds_file.exists():
        print("Ready to run with Google Sheets integration")
    else:
        print("Can run with test endpoints only (no Google Sheets)")


def setup_development():
    """Set up development environment."""
    print("Setting up development environment...")

    # Create directories
    dirs = ["credentials", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created {dir_name}/ directory")

    # Copy credential template if not exists
    creds_example = Path("credentials") / "google-credentials.json.example"
    creds_file = Path("credentials") / "google-credentials.json"

    if creds_example.exists() and not creds_file.exists():
        print(f"\nTo complete setup:")
        print(f"1. Get Google Service Account credentials")
        print(f"2. Save them as: {creds_file}")
        print(f"3. Update config.py with editor emails")

    print("\nDevelopment setup complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_development()
    else:
        check_setup()
