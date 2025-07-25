#!/usr/bin/env python3
"""
Production server runner for Finance SMS Logger Flask Application.
Uses Waitress WSGI server for production deployment.
"""

import os
import sys
import argparse
import signal
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def setup_environment():
    """Setup environment and load configuration."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env file loading")


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import waitress

        print("✅ Waitress WSGI server available")
        return True
    except ImportError:
        print("❌ Waitress not installed")
        print("Install it with: pip install waitress")
        return False


def validate_configuration():
    """Validate application configuration."""
    try:
        from config import AppConfig, get_env_variable

        print("🔧 Validating configuration...")

        # Check API key
        api_key = get_env_variable("API_KEY")
        if not api_key:
            print("⚠️  API_KEY not set - API endpoints will not work")
        else:
            print("✅ API_KEY configured")

        # Check Google Sheets configuration
        workbook_id = get_env_variable("GSHEET_SHARED_WORKBOOK_ID")
        if not workbook_id or workbook_id == "your-shared-workbook-id-here":
            print("⚠️  GSHEET_SHARED_WORKBOOK_ID not configured")
        else:
            print("✅ Google Sheets workbook configured")

        # Check Google credentials
        google_vars = ["GOOGLE_PROJECT_ID", "GOOGLE_CLIENT_EMAIL", "GOOGLE_PRIVATE_KEY"]
        missing_google = [var for var in google_vars if not get_env_variable(var)]
        if missing_google:
            print(f"⚠️  Missing Google credentials: {missing_google}")
        else:
            print("✅ Google credentials configured")

        print(
            f"📊 Configuration: Debug={AppConfig.DEBUG}, Log Level={AppConfig.LOG_LEVEL}"
        )

        return True

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    try:
        from config import AppConfig

        # Create logs directory
        os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)
        print(f"📁 Logs directory: {AppConfig.LOGS_DIR}")

        # Create credentials directory (in case needed for file-based credentials)
        credentials_dir = project_dir / "credentials"
        credentials_dir.mkdir(exist_ok=True)
        print(f"📁 Credentials directory: {credentials_dir}")

        return True

    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False


def setup_signal_handlers(server_process=None):
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        if server_process:
            server_process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_waitress_server(host="0.0.0.0", port=5000, threads=6, **kwargs):
    """Run the Flask application with Waitress."""
    try:
        from waitress import serve
        from app import app

        print("Finance SMS Logger - Production Server")
        print("=" * 60)
        print(f"🚀 Starting Waitress WSGI server")
        print(f"🌐 Server URL: http://{host}:{port}")
        print(f"🧵 Threads: {threads}")
        print(f"📊 Environment: Production")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)

        # Setup signal handlers
        setup_signal_handlers()

        # Default Waitress configuration optimized for production
        waitress_config = {
            "host": host,
            "port": port,
            "threads": threads,
            "connection_limit": 1000,
            "cleanup_interval": 30,
            "channel_timeout": 120,
            "log_untrusted_proxy_headers": True,
            "clear_untrusted_proxy_headers": True,
            "ident": "Finance-SMS-Logger/1.0",
            **kwargs,  # Allow override of any configuration
        }

        # Start the server
        serve(app, **waitress_config)

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def run_with_systemd():
    """Run with systemd-friendly configuration."""
    print("🔧 Running in systemd mode")
    run_waitress_server(
        host="0.0.0.0", port=5000, threads=8, connection_limit=2000, cleanup_interval=60
    )


def run_with_docker():
    """Run with Docker-friendly configuration."""
    print("🐳 Running in Docker mode")
    run_waitress_server(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        threads=6,
        connection_limit=1000,
    )


def run_performance_mode():
    """Run with high-performance configuration."""
    print("⚡ Running in performance mode")
    import multiprocessing

    optimal_threads = multiprocessing.cpu_count() * 2
    run_waitress_server(
        host="0.0.0.0",
        port=5000,
        threads=optimal_threads,
        connection_limit=2000,
        cleanup_interval=15,
        channel_timeout=60,
    )


def run_light_mode():
    """Run with lightweight configuration."""
    print("💡 Running in light mode")
    run_waitress_server(
        host="0.0.0.0",
        port=5000,
        threads=1,
        connection_limit=500,
        cleanup_interval=60,
        channel_timeout=120,
    )


def run_basic():
    """Run with basic configuration."""
    print("🔧 Running in basic mode")
    run_waitress_server()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Finance SMS Logger Production Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python production.py                    # Basic production server
  python production.py --mode light       # Lightweight mode (no heavy optimizations)
  python production.py --mode performance # High-performance mode
  python production.py --mode systemd     # Systemd-friendly mode
  python production.py --mode docker      # Docker-friendly mode
  python production.py --host 127.0.0.1 --port 8000 --threads 4
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["basic", "light", "performance", "systemd", "docker"],
        default="basic",
        help="Server configuration mode",
    )

    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port", type=int, default=5000, help="Port to bind to (default: 5000)"
    )

    parser.add_argument(
        "--threads", type=int, default=6, help="Number of threads (default: 6)"
    )

    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip configuration validation"
    )

    args = parser.parse_args()

    print("🚀 Finance SMS Logger Production Server")
    print("=" * 50)

    # Setup environment
    setup_environment()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Validate configuration
    if not args.skip_checks:
        if not validate_configuration():
            print("⚠️  Configuration issues found. Use --skip-checks to ignore.")
            sys.exit(1)

    # Create directories
    if not create_directories():
        sys.exit(1)

    # Run server based on mode
    try:
        if args.mode == "systemd":
            run_with_systemd()
        elif args.mode == "docker":
            run_with_docker()
        elif args.mode == "performance":
            run_performance_mode()
        elif args.mode == "light":
            run_light_mode()
        else:
            # Basic mode or custom configuration
            run_waitress_server(host=args.host, port=args.port, threads=args.threads)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
