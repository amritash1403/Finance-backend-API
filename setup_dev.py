"""
Development setup script for Finance SMS Logger.
Helps with initial setup and testing.
"""

import os
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment_variables():
    """Check if environment variables are properly configured."""
    print("\n🔧 ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)

    # Required environment variables with their default values from config
    required_env_vars = {
        "SECRET_KEY": "your-secret-key-here-change-in-production",
        "API_KEY": "your-secure-api-key-here",
        "GSHEET_SHARED_WORKBOOK_ID": "your-shared-workbook-id-here",
        # Google Service Account credentials (required for deployment)
        "GOOGLE_PROJECT_ID": None,
        "GOOGLE_PRIVATE_KEY_ID": None,
        "GOOGLE_PRIVATE_KEY": None,
        "GOOGLE_CLIENT_EMAIL": None,
        "GOOGLE_CLIENT_ID": None,
    }

    # Optional environment variables with defaults
    optional_env_vars = {
        "DEBUG": "True",
        "LOG_LEVEL": "INFO",
        "API_VERSION": "v1",
        "MAX_SMS_LENGTH": "1000",
        "MIN_SMS_LENGTH": "10",
    }

    env_status = {"missing_required": [], "using_defaults": [], "configured": []}

    # Check required variables
    for var, default_value in required_env_vars.items():
        current_value = os.getenv(var)

        if not current_value:
            env_status["missing_required"].append(var)
            print(f"✗ {var}: NOT SET (required)")
        elif current_value == default_value:
            env_status["using_defaults"].append(var)
            print(f"⚠️  {var}: Using default value (should be changed for production)")
        else:
            env_status["configured"].append(var)
            print(f"✓ {var}: Configured")

    # Check optional variables
    for var, default_value in optional_env_vars.items():
        current_value = os.getenv(var)

        if not current_value:
            print(f"ℹ️  {var}: Using default ({default_value})")
        elif current_value == default_value:
            print(f"ℹ️  {var}: Using default ({default_value})")
        else:
            print(f"✓ {var}: Custom value set")

    # Summary
    print("\n" + "=" * 50)
    if env_status["missing_required"]:
        print("❌ ENVIRONMENT SETUP INCOMPLETE")
        print(
            f"Missing required variables: {', '.join(env_status['missing_required'])}"
        )
        print("Please update your .env file with proper values.")
        return False
    elif env_status["using_defaults"]:
        print("⚠️  ENVIRONMENT SETUP NEEDS ATTENTION")
        print(f"Using default values: {', '.join(env_status['using_defaults'])}")
        print("These should be changed for production use.")
        return True
    else:
        print("✅ ENVIRONMENT SETUP COMPLETE")
        print("All required variables are properly configured.")
        return True


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

    # Check environment variables
    env_check_passed = check_environment_variables()

    print("\n" + "=" * 50)
    print("Setup Status Summary:")

    if creds_file.exists():
        print("✓ Google credentials available")
    else:
        print("⚠️  Google credentials missing (test mode only)")

    if env_check_passed:
        print("✓ Environment variables configured")
    else:
        print("❌ Environment variables need attention")

    return env_check_passed and creds_file.exists()


def setup_development():
    """Set up development environment."""
    print("Setting up development environment...")

    # Create directories
    dirs = ["credentials", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created {dir_name}/ directory")

    # Copy .env.example to .env if .env doesn't exist
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_example.exists() and not env_file.exists():
        shutil.copy2(env_example, env_file)
        print(f"✓ Created .env from .env.example")
        print(f"⚠️  Please update .env with your actual values")

    # Copy credential template if not exists
    creds_example = Path("credentials") / "google-credentials.json.example"
    creds_file = Path("credentials") / "google-credentials.json"

    if creds_example.exists() and not creds_file.exists():
        print(f"\nTo complete setup:")
        print(f"1. Get Google Service Account credentials")
        print(f"2. Save them as: {creds_file}")
        print(f"3. Update .env with proper values")

    print("\nDevelopment setup complete!")
    print("Run 'python setup_dev.py' to check configuration status.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_development()
    else:
        is_ready = check_setup()

        if not is_ready:
            print("\n💡 NEXT STEPS:")
            print("1. Run 'python setup_dev.py setup' to create missing files")
            print("2. Update .env with your actual values")
            print("3. Add Google credentials if needed")
            print("4. Run 'python setup_dev.py' again to verify")
        else:
            print("\n🚀 System is ready to run!")
            print("You can start the application with: python app.py")
