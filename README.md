# Finance SMS Logger API

A Flask-based API for parsing and logging financial SMS messages to Google Sheets with API key authentication.

## Features

- Parse financial SMS messages to extract transaction details
- Log parsed data to Google Sheets automatically
- API key authentication for secure access
- Comprehensive test coverage
- Real-time health monitoring

## Quick Start

### 1. Environment Setup

1. Copy the example environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Update `.env` with your configuration:
   ```env
   SECRET_KEY=your-secure-secret-key
   API_KEY=your-secure-api-key-here
   SHARED_WORKBOOK_ID=your-google-sheets-id
   EDITOR_EMAILS=your-email@example.com
   ```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the Application

```powershell
python app.py
```

The API will be available at `http://localhost:5000`

## Authentication

All API endpoints (except `/health`) require authentication using the `X-API-KEY` header:

```bash
# Valid request
curl -X POST http://localhost:5000/api/v1/sms \
  -H "X-API-KEY: your-secure-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your SMS message here"}'

# Health check (no auth required)
curl http://localhost:5000/health
```

## API Endpoints

| Endpoint      | Method | Auth Required | Description               |
| ------------- | ------ | ------------- | ------------------------- |
| `/health`     | GET    | No            | Health check endpoint     |
| `/api/v1/sms` | POST   | Yes           | Parse and log SMS message |

See `endpoints.md` for detailed API documentation with examples.

## Testing

Run all tests:

```powershell
python run_tests.py
```

Run specific test categories:

```powershell
# Authentication tests only
python test_authentication.py

# SMS parsing tests only
python test_sms_parser.py
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- `API_KEY`: Required for API authentication
- `SECRET_KEY`: Flask secret key for sessions
- `SHARED_WORKBOOK_ID`: Google Sheets workbook ID
- `EDITOR_EMAILS`: Comma-separated list of authorized editor emails
- `DEBUG`: Enable/disable debug mode (default: True)
- `LOG_LEVEL`: Logging level (default: INFO)

## Security

- API key authentication protects all API endpoints
- Environment variable configuration keeps secrets secure
- Comprehensive input validation and error handling
- Structured logging for security monitoring

## Project Structure

```
Finance/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── endpoints.md          # API documentation
├── requirements.txt      # Python dependencies
├── run_tests.py         # Comprehensive test suite
├── test_authentication.py # Authentication tests
├── test_sms_parser.py   # SMS parsing tests
└── sms_parser/          # SMS parsing module
    ├── engine.py        # Main parsing engine
    ├── models.py        # Data models
    ├── utils.py         # Utility functions
    └── ...              # Other parsing modules
```

## Development

For development with automatic reloading:

```powershell
$env:FLASK_ENV="development"; python app.py
```

## Troubleshooting

### Common Issues

1. **Authentication Errors (403)**

   - Verify `API_KEY` is set in `.env`
   - Check `X-API-KEY` header in requests
   - Ensure header value matches environment variable

2. **Google Sheets Access**

   - Verify `SHARED_WORKBOOK_ID` is correct
   - Check `EDITOR_EMAILS` includes your email
   - Ensure Google Sheets API is enabled

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

### Debug Mode

Enable debug mode for detailed error messages:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License.
