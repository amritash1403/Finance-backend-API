# Production Deployment Guide

This guide covers deploying the Finance SMS Logger application in production using Waitress WSGI server.

## Quick Start

### Windows

```cmd
# Option 1: PowerShell
.\start_production.ps1

# Option 2: Batch file
start_production.bat

# Option 3: Direct command
python production.py --mode performance
```

### Linux/Mac

```bash
# Option 1: Shell script
./start_production.sh

# Option 2: Direct command
python production.py --mode performance
```

## Production Server Commands

### Basic Production Server

```bash
python production.py
```

### High-Performance Mode

```bash
python production.py --mode performance
```

### Custom Configuration

```bash
python production.py --host 0.0.0.0 --port 8000 --threads 8
```

### Systemd Mode (Linux)

```bash
python production.py --mode systemd
```

### Docker Mode

```bash
python production.py --mode docker
```

## Server Modes

### Basic Mode

- **Threads**: 6
- **Connections**: 1000
- **Best for**: Small to medium applications

### Performance Mode

- **Threads**: CPU cores × 2
- **Connections**: 2000
- **Cleanup interval**: 15 seconds
- **Best for**: High-traffic applications

### Systemd Mode

- **Threads**: 8
- **Connections**: 2000
- **Cleanup interval**: 60 seconds
- **Best for**: Linux server deployments

### Docker Mode

- **Port**: From `PORT` environment variable (default 5000)
- **Threads**: 6
- **Best for**: Containerized deployments

## Environment Variables

### Required

```bash
API_KEY=your-api-key-here
GSHEET_SHARED_WORKBOOK_ID=your-workbook-id
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_PRIVATE_KEY_ID=key-id
GOOGLE_CLIENT_ID=client-id
```

### Optional

```bash
DEBUG=False
LOG_LEVEL=INFO
PORT=5000
WAITRESS_THREADS=6
WAITRESS_CONNECTION_LIMIT=1000
```

## Deployment Options

### 1. Direct Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
python production.py --mode performance
```

### 2. Systemd Service (Linux)

```bash
# Copy service file
sudo cp finance-sms-logger.service /etc/systemd/system/

# Edit paths in service file
sudo nano /etc/systemd/system/finance-sms-logger.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable finance-sms-logger
sudo systemctl start finance-sms-logger

# Check status
sudo systemctl status finance-sms-logger
```

### 3. Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN chmod +x docker-entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]
```

### 4. Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Tuning

### Thread Configuration

```bash
# Conservative (low memory)
python production.py --threads 4

# Balanced (default)
python production.py --threads 6

# High performance (more CPU/memory)
python production.py --threads 12
```

### Connection Limits

- Default: 1000 concurrent connections
- High traffic: Use `--mode performance` for 2000 connections
- Configure via `WAITRESS_CONNECTION_LIMIT` environment variable

### Memory Optimization

- Monitor memory usage with the performance monitor
- Adjust threads based on available RAM
- Use systemd limits for production deployments

## Monitoring

### Health Check

```bash
curl http://localhost:5000/health
```

### Performance Monitoring

```bash
# Run performance tests
python performance_monitor.py

# Check server logs
tail -f logs/waitress_*.log
```

### System Resources

```bash
# Check process status
ps aux | grep python

# Monitor resource usage
htop
```

## Troubleshooting

### Common Issues

1. **Port already in use**

   ```bash
   python production.py --port 8000
   ```

2. **Permission denied**

   ```bash
   # Linux: Use non-privileged port
   python production.py --port 8080
   ```

3. **High memory usage**

   ```bash
   # Reduce threads
   python production.py --threads 4
   ```

4. **Slow response times**
   ```bash
   # Increase threads
   python production.py --mode performance
   ```

### Logs

- Application logs: `logs/app.log`
- Server logs: Console output
- System logs: `/var/log/syslog` (Linux)

## Security Considerations

1. **Environment Variables**: Store sensitive data in environment variables, not code
2. **Reverse Proxy**: Use Nginx/Apache for SSL termination
3. **Firewall**: Restrict access to application port
4. **Updates**: Keep dependencies updated regularly

## Backup and Recovery

1. **Environment Configuration**: Backup `.env` file
2. **Google Credentials**: Backup service account key
3. **Application Data**: Google Sheets data is automatically backed up
4. **Logs**: Regular log rotation and archival

## Support

For issues and questions:

1. Check logs for error messages
2. Verify environment configuration
3. Test with development server first
4. Review this documentation
