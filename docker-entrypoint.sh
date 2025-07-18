#!/bin/bash
# Docker entrypoint script for Finance SMS Logger
# This script prepares the environment and starts the application with Waitress

set -e

echo "🐳 Finance SMS Logger - Docker Container Starting"
echo "================================================"

# Function to handle signals for graceful shutdown
cleanup() {
    echo "🛑 Received shutdown signal, stopping application..."
    if [ ! -z "$APP_PID" ]; then
        kill -TERM "$APP_PID" 2>/dev/null || true
        wait "$APP_PID" 2>/dev/null || true
    fi
    echo "✅ Application stopped gracefully"
    exit 0
}

# Setup signal handlers
trap cleanup SIGTERM SIGINT

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p credentials

# Check required environment variables
echo "🔧 Checking environment variables..."
if [ -z "$API_KEY" ]; then
    echo "⚠️  Warning: API_KEY not set"
fi

if [ -z "$GSHEET_SHARED_WORKBOOK_ID" ]; then
    echo "⚠️  Warning: GSHEET_SHARED_WORKBOOK_ID not set"
fi

# Run database migrations or setup if needed
echo "🔧 Running application setup..."
python -c "
try:
    from config import AppConfig
    import os
    print(f'✅ Configuration loaded: Debug={AppConfig.DEBUG}')
    
    # Test Google credentials if available
    try:
        from config import get_google_credentials_info
        get_google_credentials_info()
        print('✅ Google credentials validated')
    except Exception as e:
        print(f'⚠️  Google credentials issue: {e}')
        
except Exception as e:
    print(f'❌ Setup error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Application setup failed"
    exit 1
fi

echo "🚀 Starting application with Waitress..."
echo "================================================"

# Start the application in background and get PID
python production.py --mode docker &
APP_PID=$!

echo "✅ Application started with PID: $APP_PID"
echo "🌐 Server should be available on port ${PORT:-5000}"

# Wait for the application to finish
wait "$APP_PID"
