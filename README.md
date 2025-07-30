# Finance SMS Logger API

A Flask-based REST API for parsing SMS transactions and logging them to Google Sheets. This application automatically extracts transaction information from bank SMS messages and organizes them in monthly spreadsheets with categorization and spending analytics.

## 🌟 Features

- **SMS Transaction Parsing**: Intelligent parsing of bank SMS messages to extract transaction details
- **Google Sheets Integration**: Automatic logging to organized monthly spreadsheets
- **RESTful API**: Complete CRUD operations for transaction management
- **Spending Analytics**: Monthly spending statistics with category breakdowns
- **Secure Authentication**: API key-based authentication
- **Production Ready**: Optimized for deployment on cloud platforms
- **Caching**: Built-in caching for improved performance

## 📱 Android App

This API works with the companion Android app available at:
**[Finance App Android](https://github.com/Satyajit-2003/Finance-App-Android/)**

Download the latest release from the GitHub repository and configure it with your API details.

## 🚀 Quick Deploy to Render

> 💡 **Perfect for Personal Use**: This setup works great on Render's **FREE TIER** - ideal for personal finance tracking without any monthly costs!

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Google Sheets API Setup](#step-1-google-sheets-api-setup)
- [Step 2: Environment Configuration](#step-2-environment-configuration)
- [Step 3: Deploy to Render](#step-3-deploy-to-render)
- [Step 4: Configure Android App](#step-4-configure-android-app)
- [API Documentation](#api-documentation)
- [Local Development](#local-development)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [ ] A Google account
- [ ] A GitHub account (for free Render deployment)
- [ ] Basic understanding of environment variables
- [ ] An Android device for the companion app

> 💰 **Cost**: Everything in this guide uses **FREE TIERS** - no credit card required!

---

## Step 1: Google Sheets API Setup

### 1.1 Create Google Cloud Project

1. **Go to Google Cloud Console**

   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create New Project**

   - Click on the project dropdown (top-left)
   - Click "New Project"
   - Enter project name: `finance-sms-logger` (Or anything you prefer)
   - Click "Create"

3. **Select Your Project**
   - Wait for project creation to complete
   - Select your new project from the dropdown

### 1.2 Enable Google Sheets API

1. **Navigate to APIs & Services**

   - In the left sidebar, click "APIs & Services" → "Library"

2. **Search for Google Sheets API**

   - In the search box, type "Google Sheets API"
   - Click on "Google Sheets API" from results
   - Click "Enable"

3. **Wait for API to Enable**
   - This may take a few moments

### 1.3 Create Service Account

1. **Go to Credentials**

   - In the left sidebar, click "APIs & Services" → "Credentials"

2. **Create Service Account**

   - Click "Create Credentials" → "Service Account"
   - Service account name: `finance-sheets-service`
   - Service account ID: `finance-sheets-service` (auto-filled)
   - Description: `Service account for Finance SMS Logger`
   - Click "Create and Continue"

3. **Grant Permissions (Optional)**

   - Skip this step by clicking "Continue"

4. **Generate Key**

   - Click "Done" to create the service account
   - Find your new service account in the list
   - Click on the service account email
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

5. **Download JSON Key**
   - A JSON file will be downloaded automatically
   - **⚠️ IMPORTANT**: Keep this file secure - it contains your private keys
   - Rename it to `google-credentials.json` for easy reference

### 1.4 Extract Required Information

Open the downloaded JSON file and note down these values:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "finance-sheets-service@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  ...
}
```

**You'll need**:

- `project_id`
- `private_key_id`
- `private_key` (entire string including newlines)
- `client_email`
- `client_id`

---

## Step 2: Environment Configuration

### 2.1 Download Environment Template

1. **Get the .env.example file**

   - Go to this repository
   - Download or copy the contents of `.env.example`

2. **Create your .env file**
   - Create a new file named `.env`
   - Copy the contents from `.env.example`

### 2.2 Configure Environment Variables

Fill in your `.env` file with these values:

```bash
# API Configuration
API_KEY=your_secure_api_key_here_min_16_chars

# Google Sheets Configuration
GSHEET_SHARED_WORKBOOK_ID=your_spreadsheet_id_here

# Google API Credentials
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour full private key here\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=finance-sheets-service@your-project-id.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id

# Production Settings
DEBUG=False
LOG_LEVEL=INFO
```

### 2.3 Generate API Key

**Create a secure API key**:

```bash
# Option 1: Random string (minimum 16 characters)
API_KEY=your_secure_api_key_here_min_16_chars

# Option 2: Generate using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**⚠️ Security Notes**:

- Use a unique, random API key
- Minimum 16 characters
- Include letters, numbers, and special characters
- Keep it secret and secure

### 2.4 Create Google Spreadsheet

1. **Create New Spreadsheet**

   - Go to [Google Sheets](https://sheets.google.com)
   - Click "Blank" to create new spreadsheet
   - Name it: `Finance SMS Logger`

2. **Get Spreadsheet ID**

   - Copy the URL of your spreadsheet
   - Extract the ID from the URL:

   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL/edit
                                          ^^^^^^^^^^^^^^^^^^^^^^
                                            This is your ID
   ```

3. **Share with Service Account**

   - Click "Share" button (top-right)
   - In "Add people and groups", paste your service account email:
     `finance-sheets-service@your-project-id.iam.gserviceaccount.com`
   - **⚠️ IMPORTANT**: Set permission to "Editor"
   - Click "Share"

4. **Update .env file**
   ```bash
   GSHEET_SHARED_WORKBOOK_ID=1ABC123DEF456GHI789JKL
   ```

---

## Step 3: Deploy to Render

### 3.1 Fork Repository

1. **Fork this repository**
   - Click "Fork" button on this GitHub page
   - Select your GitHub account
   - Wait for fork to complete

### 3.2 Create Render Account

1. **Sign up for Render**

   - Go to [render.com](https://render.com)
   - Click "Get Started for Free"
   - Sign up with GitHub (recommended)
   - **✨ Free Tier Includes**:
     - 750 hours/month of compute time
     - Automatic HTTPS
     - Git-based deployments
     - Perfect for personal projects!
     - Use UptimeBot to keep your service awake

2. **Connect GitHub**
   - Authorize Render to access your repositories
   - Select "All repositories" or specific repositories

### 3.3 Deploy Web Service

1. **Create New Web Service**

   - On Render dashboard, click "New +"
   - Select "Web Service"

2. **Connect Repository**

   - Find your forked repository: `your-username/Finance-backend-API`
   - Click "Connect"

3. **Configure Service**

   ```
   Name: finance-sms-logger
   Region: Select closest to your location
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python production.py --mode light
   ```

4. **Set Instance Type**
   - **Free Tier**: Select "Free" ⭐ **RECOMMENDED for personal projects**
     - 750 hours/month (enough for continuous use)
     - Automatic sleep after 15 minutes of inactivity
     - Perfect for personal finance tracking
   - **Paid Tier**: Select "Starter" ($7/month) only if you need 24/7 uptime

### 3.4 Configure Environment Variables

**🎯 EASY METHOD: Upload .env File (Recommended)**

1. **Prepare Your .env File**

   - Make sure your `.env` file is complete with all variables
   - Double-check all values are correct

2. **Upload .env File to Render**
   - In your service settings, click "Environment" tab
   - Look for "Add from .env" or "Upload .env" button
   - Click and select your `.env` file
   - Render will automatically parse and add all variables
   - Review the imported variables to ensure they're correct

**📝 MANUAL METHOD: Add Variables Individually**

If the upload option isn't available, add each variable manually:

1. **Go to Environment Tab**

   - In your service settings, click "Environment"

2. **Add Environment Variables**
   Add each variable from your `.env` file:

   | Key                         | Value                                                             |
   | --------------------------- | ----------------------------------------------------------------- |
   | `API_KEY`                   | `your_secure_api_key_here`                                        |
   | `GSHEET_SHARED_WORKBOOK_ID` | `your_spreadsheet_id`                                             |
   | `GOOGLE_PROJECT_ID`         | `your-project-id`                                                 |
   | `GOOGLE_PRIVATE_KEY_ID`     | `your-private-key-id`                                             |
   | `GOOGLE_PRIVATE_KEY`        | `"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"` |
   | `GOOGLE_CLIENT_EMAIL`       | `your-service-account-email`                                      |
   | `GOOGLE_CLIENT_ID`          | `your-client-id`                                                  |
   | `DEBUG`                     | `False`                                                           |
   | `LOG_LEVEL`                 | `INFO`                                                            |

   **⚠️ Critical Notes**:

   - For `GOOGLE_PRIVATE_KEY`: Include the quotes and preserve all newlines (`\n`)
   - Copy-paste the exact private key from your JSON file
   - Double-check all values for typos

3. **Save Environment Variables**
   - Click "Save Changes"

### 3.5 Deploy and Monitor

1. **Start Deployment**

   - Click "Create Web Service"
   - Render will start building and deploying your app

2. **Monitor Build Process**

   - Watch the build logs for any errors
   - Deployment typically takes 3-5 minutes
   - **Free Tier Note**: First deployment may take slightly longer

3. **Check Deployment Status**

   - Wait for "Your service is live" message
   - Note your service URL: `https://your-service-name.onrender.com`

4. **Test Your API**

   ```bash
   # Test health endpoint
   curl https://your-service-name.onrender.com/health

   # Expected response:
   {
     "status": "healthy",
     "timestamp": "YYYY-MM-DD T...",
     "version": "1.0.0"
   }
   ```

**💡 Free Tier Behavior**:

- Service sleeps after 15 minutes of inactivity
- First request after sleep may take 10-30 seconds to wake up
- Perfect for personal use - the Android app will wake it automatically
- 750 hours/month limit (more than enough for continuous personal use)

---

## Step 4: Configure Android App

### 4.1 Download Android App

1. **Get the App**

   - Visit [Finance App Android Releases](https://github.com/Satyajit-2003/Finance-App-Android/releases)
   - Download the latest APK file
   - Install on your Android device

2. **Install APK**
   - Enable "Install from Unknown Sources" if needed
   - Open the downloaded APK file
   - Follow installation prompts

### 4.2 Configure App Settings

1. **Open App Settings**

   - Launch the Finance App
   - Go to "Settings" tab

2. **Enter API Configuration**

   ```
   API URL: https://your-service-name.onrender.com
   API Key: your_secure_api_key_here
   ```

3. **Test Connection**
   - Use the "Test Connection" button in settings
   - Verify successful connection to your API

### 4.3 Grant Permissions

1. **SMS Permissions**

   - Grant SMS read permissions when prompted
   - This allows the app to read SMS messages

2. **Notification Permissions**
   - Grant notification permissions for transaction alerts

---

3. **Check Server Logs**

   - In Render dashboard, go to your service
   - Click "Logs" tab to view real-time logs

4. **Verify Environment Variables**
   - In Render dashboard, check "Environment" tab
   - Ensure all required variables are set

### Getting Help

If you encounter issues:

1. **Check Logs**: Always check server logs first
2. **Test Locally**: Try running the API locally to isolate issues
3. **Verify Configuration**: Double-check all environment variables
4. **API Documentation**: Review `endpoints.md` for correct usage
5. **GitHub Issues**: Create an issue with detailed error information

---

## Security Considerations

### Production Security

- **API Keys**: Use strong, unique API keys (minimum 16 characters)
- **HTTPS**: Always use HTTPS in production (Render provides this automatically)
- **Environment Variables**: Never commit sensitive data to version control
- **Service Account**: Limit service account permissions to only required sheets

### Best Practices

- **Regular Updates**: Keep dependencies updated
- **Log Monitoring**: Monitor application logs for suspicious activity
- **Access Control**: Only share API credentials with authorized users
- **Backup**: Google Sheets provides automatic backup, but consider additional backups

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

- **Documentation**: Check `endpoints.md` and `README-dev.txt`
- **Issues**: Create GitHub issues for bugs and feature requests
- **Android App**: Check the [Android app repository](https://github.com/Satyajit-2003/Finance-App-Android/) for app-specific issues

---

**Happy tracking! 🎉**
