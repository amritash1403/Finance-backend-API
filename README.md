# Finance SMS Logger API

A Flask-based API for parsing and logging financial SMS messages to Google Sheets with API key authentication.

## Features

- Parse financial SMS messages to extract transaction details
- Log parsed data to Google Sheets automatically
- **Dynamic Google credentials generation** - no file uploads needed for deployment
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
   GSHEET_SHARED_WORKBOOK_ID=your-google-sheets-id
   EDITOR_EMAILS=your-email@example.com

   # Google Service Account (for dynamic credentials)
   GOOGLE_PROJECT_ID=your-project-id
   GOOGLE_PRIVATE_KEY_ID=your-private-key-id
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
   GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
   GOOGLE_CLIENT_ID=your-client-id
   ```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the Application

**Development Mode:**

```powershell
python app.py
```

**Production Mode:**

```powershell
python production.py
```

The API will be available at `http://localhost:5000` (development) or configured production host/port.

## Authentication

All API endpoints (except `/health`) require authentication using the `X-API-KEY` header:

```bash
# Valid request
curl -X POST http://localhost:5000/api/v1/log \
  -H "X-API-KEY: your-secure-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your SMS message here"}'

# Health check (no auth required)
curl http://localhost:5000/health
```

## API Endpoints

| Endpoint                      | Method | Auth Required | Description                     |
| ----------------------------- | ------ | ------------- | ------------------------------- |
| `/health`                     | GET    | No            | Health check endpoint           |
| `/api/v1/log`                 | POST   | Yes           | Log SMS transaction             |
| `/api/v1/parse-sms`           | POST   | Yes           | Test SMS parsing                |
| `/api/v1/sheets/{month-year}` | GET    | Yes           | Get sheet information           |
| `/api/v1/stats/{month-year}`  | GET    | Yes           | Get monthly spending statistics |

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
- `GSHEET_SHARED_WORKBOOK_ID`: Google Sheets workbook ID
- `GOOGLE_PROJECT_ID`, `GOOGLE_PRIVATE_KEY`, etc.: Google Service Account credentials
- `EDITOR_EMAILS`: Comma-separated list of authorized editor emails
- `DEBUG`: Enable/disable debug mode (default: True)
- `LOG_LEVEL`: Logging level (default: INFO)

### Google Credentials

The app supports **two methods** for Google authentication:

1. **Static file**: Place `google-credentials.json` in `credentials/` folder
2. **Dynamic generation**: Set `GOOGLE_*` environment variables (recommended for deployment)

See `DEPLOYMENT.md` for detailed deployment instructions.

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
