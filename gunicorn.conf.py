# Gunicorn configuration file for production deployment
# Save this as gunicorn.conf.py

import os
import multiprocessing
from pathlib import Path

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

accesslog = str(log_dir / "gunicorn_access.log")
errorlog = str(log_dir / "gunicorn_error.log")
loglevel = os.getenv("LOG_LEVEL", "INFO").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "finance-sms-logger"

# Server mechanics
daemon = False
pidfile = str(log_dir / "gunicorn.pid")
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
capture_output = True
enable_stdio_inheritance = True
