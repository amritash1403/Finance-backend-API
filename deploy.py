"""
Production deployment helper for Finance SMS Logger.
"""

import os
import json
from pathlib import Path


def check_production_readiness():
    """Check if the application is ready for production."""
    print("Production Readiness Check")
    print("=" * 50)

    issues = []

    # Check environment variables
    if os.getenv("SECRET_KEY") == "your-secret-key-here-change-in-production":
        issues.append("SECRET_KEY not set in environment")

    # Check Google credentials
    creds_file = Path("credentials") / "google-credentials.json"
    if not creds_file.exists():
        issues.append("Google credentials file missing")

    # Check config
    try:
        from config import SheetConfig

        if "your-email@example.com" in SheetConfig.EDITOR_EMAILS:
            issues.append("Editor emails not configured")
    except ImportError:
        issues.append("Config module not accessible")

    # Check logs directory
    if not Path("logs").exists():
        issues.append("Logs directory missing")

    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n🔧 Fix these issues before production deployment.")
        return False
    else:
        print("✅ Application is ready for production!")
        return True


def create_production_config():
    """Create production configuration template."""
    config = {
        "environment": "production",
        "debug": False,
        "host": "0.0.0.0",
        "port": 5000,
        "workers": 4,
        "timeout": 30,
        "max_requests": 1000,
        "log_level": "INFO",
        "access_log": True,
    }

    with open("production_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Created production_config.json")


def create_systemd_service():
    """Create systemd service file for Linux deployment."""

    service_content = f"""[Unit]
Description=Finance SMS Logger Flask App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={Path.cwd()}
Environment=PATH={Path.cwd() / 'venv' / 'bin'}
ExecStart={Path.cwd() / 'venv' / 'bin' / 'gunicorn'} -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    with open("finance-sms-logger.service", "w") as f:
        f.write(service_content)

    print("Created systemd service file: finance-sms-logger.service")
    print("To install:")
    print("  sudo cp finance-sms-logger.service /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable finance-sms-logger")
    print("  sudo systemctl start finance-sms-logger")


def create_nginx_config():
    """Create nginx configuration for reverse proxy."""

    nginx_content = """server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout       60s;
        proxy_send_timeout          60s;
        proxy_read_timeout          60s;
        
        # Buffer settings
        proxy_buffer_size           4k;
        proxy_buffers               4 32k;
        proxy_busy_buffers_size     64k;
    }
    
    # Static files (if any)
    location /static {
        alias /path/to/your/static/files;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# HTTPS redirect (optional)
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

    with open("nginx.conf", "w") as f:
        f.write(nginx_content)

    print("Created nginx configuration: nginx.conf")


def create_docker_files():
    """Create Docker configuration files."""

    dockerfile = """FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
"""

    docker_compose = """version: '3.8'

services:
  finance-sms-logger:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./credentials:/app/credentials:ro
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - finance-sms-logger
    restart: unless-stopped
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)

    print("Created Docker files: Dockerfile, docker-compose.yml")


def create_deployment_scripts():
    """Create deployment scripts."""

    deploy_script = """#!/bin/bash
# Deployment script for Finance SMS Logger

set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run tests
python simple_test.py

# Check production readiness
python deploy.py check

# Restart service
sudo systemctl restart finance-sms-logger

# Check status
sudo systemctl status finance-sms-logger

echo "Deployment complete!"
"""

    with open("deploy.sh", "w") as f:
        f.write(deploy_script)

    os.chmod("deploy.sh", 0o755)
    print("Created deployment script: deploy.sh")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            check_production_readiness()
        elif command == "config":
            create_production_config()
        elif command == "systemd":
            create_systemd_service()
        elif command == "nginx":
            create_nginx_config()
        elif command == "docker":
            create_docker_files()
        elif command == "scripts":
            create_deployment_scripts()
        elif command == "all":
            create_production_config()
            create_systemd_service()
            create_nginx_config()
            create_docker_files()
            create_deployment_scripts()
            print("\\nAll production files created!")
        else:
            print("Unknown command. Use: check|config|systemd|nginx|docker|scripts|all")
    else:
        print("Finance SMS Logger - Production Deployment Helper")
        print("Usage: python deploy.py [command]")
        print("Commands:")
        print("  check    - Check production readiness")
        print("  config   - Create production config")
        print("  systemd  - Create systemd service file")
        print("  nginx    - Create nginx configuration")
        print("  docker   - Create Docker files")
        print("  scripts  - Create deployment scripts")
        print("  all      - Create all production files")
