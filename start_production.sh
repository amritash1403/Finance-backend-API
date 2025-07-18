#!/bin/bash
# Production startup script for Finance SMS Logger
# This script sets up and runs the application in production mode

set -e

echo "🚀 Starting Finance SMS Logger in Production Mode"
echo "================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p credentials

echo "🌐 Starting Waitress server..."
echo "================================================="

# Run with Waitress using the production script
exec python production.py
