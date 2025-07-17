# Deployment Guide - Dynamic Google Credentials

## Overview

This application now supports **dynamic Google Service Account credentials generation** for deployment environments where uploading credential files is not possible (like many cloud platforms).

## How It Works

Instead of requiring a static `google-credentials.json` file, the application can now:

1. Generate the credentials file at runtime from environment variables
2. Use the generated file for Google Sheets API authentication
3. Automatically recreate the file if it's missing

## Environment Variables Required

Add these to your deployment environment (e.g., Heroku Config Vars, Railway environment, etc.):

### Required Google Credentials Variables

```env
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_FULL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id-number
```

### Other Required Variables

```env
SECRET_KEY=your-secure-flask-secret-key
API_KEY=your-secure-api-key
GSHEET_SHARED_WORKBOOK_ID=your-google-sheets-workbook-id
EDITOR_EMAILS=your-email@example.com
```

## Getting Your Google Credentials

1. **Create a Google Cloud Project**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Sheets API**

   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it

3. **Create Service Account**

   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create

4. **Generate Key**

   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key" > "JSON"
   - Download the JSON file

5. **Extract Values for Environment Variables**
   ```json
   {
     "type": "service_account",
     "project_id": "← GOOGLE_PROJECT_ID",
     "private_key_id": "← GOOGLE_PRIVATE_KEY_ID",
     "private_key": "← GOOGLE_PRIVATE_KEY (entire string with newlines)",
     "client_email": "← GOOGLE_CLIENT_EMAIL",
     "client_id": "← GOOGLE_CLIENT_ID"
   }
   ```

## Platform-Specific Deployment

### Heroku

```bash
heroku config:set GOOGLE_PROJECT_ID="your-project-id"
heroku config:set GOOGLE_PRIVATE_KEY_ID="your-private-key-id"
heroku config:set GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
heroku config:set GOOGLE_CLIENT_EMAIL="your-service-account@project.iam.gserviceaccount.com"
heroku config:set GOOGLE_CLIENT_ID="your-client-id"
```

### Railway

Add each variable in the Railway dashboard under "Environment Variables"

### Render

Add each variable in the Render dashboard under "Environment"

### Docker

```dockerfile
ENV GOOGLE_PROJECT_ID="your-project-id"
ENV GOOGLE_PRIVATE_KEY_ID="your-private-key-id"
ENV GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
ENV GOOGLE_CLIENT_EMAIL="your-service-account@project.iam.gserviceaccount.com"
ENV GOOGLE_CLIENT_ID="your-client-id"
```

## Testing Dynamic Credentials

Before deployment, test locally:

1. **Remove existing credentials file:**

   ```bash
   rm credentials/google-credentials.json
   ```

2. **Ensure environment variables are set in .env**

3. **Run the application:**

   ```bash
   python app.py
   ```

4. **Verify credentials are generated:**
   - Check that `credentials/google-credentials.json` is created automatically
   - Test API endpoints to ensure Google Sheets integration works

## Troubleshooting

### Missing Environment Variables

```
ValueError: Missing required environment variables: GOOGLE_PROJECT_ID, GOOGLE_PRIVATE_KEY
```

**Solution:** Ensure all 5 Google credential environment variables are set.

### Private Key Format Issues

```
Error: Invalid private key format
```

**Solution:** Ensure `GOOGLE_PRIVATE_KEY` includes the full key with `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` and proper newlines (`\n`).

### Permissions Error

```
Error: Permission denied when accessing Google Sheets
```

**Solution:**

1. Ensure the service account email is added as an editor to your Google Sheets
2. Verify `GSHEET_SHARED_WORKBOOK_ID` is correct

## Security Notes

- **Never commit `.env` files** with real credentials to version control
- **Use different credentials** for development and production
- **Regularly rotate** your service account keys
- **Limit service account permissions** to only Google Sheets API

## Benefits

✅ **No file uploads required** - works with any deployment platform  
✅ **Secure** - credentials stored as environment variables  
✅ **Automatic** - credentials generated at runtime  
✅ **Flexible** - falls back to static file if present  
✅ **Production-ready** - tested and validated
