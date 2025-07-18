# Waitress configuration file for Finance SMS Logger
# This file contains production-ready settings for the Waitress WSGI server

import os
import multiprocessing
from pathlib import Path

# Basic server settings
host = "0.0.0.0"
port = int(os.getenv("PORT", 5000))

# Thread configuration
# Waitress uses threads instead of workers like Gunicorn
threads = int(os.getenv("WAITRESS_THREADS", 6))

# Connection settings
connection_limit = int(os.getenv("WAITRESS_CONNECTION_LIMIT", 1000))
cleanup_interval = int(os.getenv("WAITRESS_CLEANUP_INTERVAL", 30))
channel_timeout = int(os.getenv("WAITRESS_CHANNEL_TIMEOUT", 120))

# Security settings
log_untrusted_proxy_headers = True
clear_untrusted_proxy_headers = True

# Server identification
ident = "Finance-SMS-Logger/1.0"

# Buffer sizes
recv_bytes = 65536
send_bytes = 65536

# Backlog for listening socket
listen = 1024

# Performance settings
# These settings are optimized for typical web application loads

# High-performance configuration (uncomment for heavy loads)
# threads = multiprocessing.cpu_count() * 2
# connection_limit = 2000
# cleanup_interval = 15
# channel_timeout = 60

# Memory-conservative configuration (uncomment for limited memory)
# threads = 4
# connection_limit = 500
# cleanup_interval = 60
# recv_bytes = 32768
# send_bytes = 32768

# Development-like configuration (uncomment for debugging)
# threads = 2
# connection_limit = 100
# cleanup_interval = 300

# URL scheme (useful behind reverse proxies)
url_scheme = os.getenv("WAITRESS_URL_SCHEME", "http")

# Trusted proxy settings (configure if behind nginx/apache)
trusted_proxy = os.getenv("WAITRESS_TRUSTED_PROXY", None)
trusted_proxy_count = (
    int(os.getenv("WAITRESS_TRUSTED_PROXY_COUNT", 1)) if trusted_proxy else None
)
trusted_proxy_headers = os.getenv("WAITRESS_TRUSTED_PROXY_HEADERS", None)

# Logging configuration
# Waitress uses Python's logging module
# Configure logging in your application, not here

# SSL settings (if using HTTPS directly with Waitress)
# ssl_cert = os.getenv("SSL_CERT_PATH", None)
# ssl_key = os.getenv("SSL_KEY_PATH", None)
