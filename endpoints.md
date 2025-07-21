# Finance SMS Logger API - Endpoints Documentation

Complete API reference for the Finance SMS Logger Flask backend service.

## 🌐 Base URL

```
http://localhost:5000
```

## 📋 API Endpoints Overview

| Endpoint                      | Method | Description                       | Authentication |
| ----------------------------- | ------ | --------------------------------- | -------------- |
| `/health`                     | GET    | Health check                      | None           |
| `/api/v1/transactions`        | POST   | Log SMS transaction               | X-API-KEY      |
| `/api/v1/parse-sms`           | POST   | Test SMS parsing                  | X-API-KEY      |
| `/api/v1/sheets/{month-year}` | GET    | Get sheet information             | X-API-KEY      |
| `/api/v1/stats/{month-year}`  | GET    | Get specific month spending stats | X-API-KEY      |
| `/api/v1/transactions/{date}` | GET    | Get transactions by date          | X-API-KEY      |
| `/api/v1/transactions`        | PATCH  | Update transaction fields         | X-API-KEY      |
| `/api/v1/transactions`        | DELETE | Delete transaction row            | X-API-KEY      |

**Note**: All API responses follow a consistent structure with `success`, `data`/`error`, and `message` fields.

## 🔐 Authentication

All API endpoints (routes starting with `/api/v1/`) require authentication using the `X-API-KEY` header. The `/health` endpoint does not require authentication.

**Required Header**:

```
X-API-KEY: your-api-key-here
```

**Authentication Errors**:

**403 Forbidden - Missing API Key**:

```json
{
  "success": false,
  "error": "Authentication required",
  "message": "X-API-KEY header is required for API endpoints"
}
```

**403 Forbidden - Invalid API Key**:

```json
{
  "success": false,
  "error": "Authentication failed",
  "message": "Invalid API key"
}
```

**500 Server Error - API Key Not Configured**:

```json
{
  "success": false,
  "error": "Authentication not configured",
  "message": "Server configuration error - contact administrator"
}
```

---

## 🔍 Endpoint Details

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the service is running and healthy.

**Parameters**: None

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-07-16T10:30:00.000Z",
  "version": "1.0.0"
}
```

**Example**:

```bash
curl http://localhost:5000/health
```

---

### 2. Log SMS Transaction

**Endpoint**: `POST /api/v1/transactions`

**Description**: Parse SMS text and log the transaction to Google Sheets.

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "text": "SMS text content",
  "date": "2025-07-14T10:30:00" // ISO format, optional (defaults to current time)
}
```

**Success Response** (201):

```json
{
  "success": true,
  "message": "Transaction logged successfully",
  "data": {
    "transaction_data": {
      "account": {
        "type": "ACCOUNT",
        "number": "3423",
        "name": null
      },
      "balance": {
        "available": "2343.23",
        "outstanding": null
      },
      "transaction": {
        "type": "debit",
        "amount": "2000.00",
        "referenceNo": null,
        "merchant": "ECS PAY"
      }
    },
    "date": "2025-07-14T10:30:00.000Z",
    "sheet_url": "https://docs.google.com/spreadsheets/d/1o__la3x...#gid=762998444"
  }
}
```

**Success Response (Invalid Transaction)** (200):

```json
{
  "success": true,
  "message": "SMS does not contain valid transaction information",
  "parsed_data": {...}
}
```

**Error Responses**:

**400 Bad Request**:

```json
{
  "success": false,
  "error": "'text' field is required",
  "message": "Bad request"
}
```

**500 Internal Server Error**:

```json
{
  "success": false,
  "error": "Database error",
  "message": "Failed to insert transaction into Google Sheets"
}
```

**503 Service Unavailable**:

```json
{
  "success": false,
  "error": "Service unavailable",
  "message": "Google Sheets service is not available"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key-here" \
  -d '{
    "text": "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
    "date": "2025-07-14T10:30:00"
  }'
```

---

### 3. Test SMS Parser

**Endpoint**: `POST /api/v1/parse-sms`

**Description**: Test SMS parsing without saving to sheets. Useful for debugging.

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "text": "SMS text content"
}
```

**Success Response** (200):

```json
{
  "success": true,
  "data": {
    "parsed_data": {
      "account": {
        "type": "ACCOUNT",
        "number": "3423",
        "name": null
      },
      "balance": {
        "available": "2343.23",
        "outstanding": null
      },
      "transaction": {
        "type": "debit",
        "amount": "2000.00",
        "referenceNo": null,
        "merchant": "ECS PAY"
      }
    },
    "is_valid_transaction": true,
    "original_text": "INR 2000 debited from A/c no. XX3423..."
  }
}
```

**Error Response** (400):

```json
{
  "success": false,
  "error": "Bad request",
  "message": "'text' field is required"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/api/v1/parse-sms \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key-here" \
  -d '{
    "text": "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23."
  }'
```

---

### 4. Get Sheet Information

**Endpoint**: `GET /api/v1/sheets/{month-year}`

**Description**: Get information about a specific monthly sheet.

**Parameters**:

- `month-year`: Month and year in format "July-2025"

**Success Response** (200):

```json
{
  "success": true,
  "data": {
    "month_year": "July-2025",
    "sheet_url": "https://docs.google.com/spreadsheets/d/1o__la3x...#gid=762998444",
    "exists": true
  }
}
```

**Sheet Not Found Response** (200):

```json
{
  "success": true,
  "data": {
    "month_year": "June-2025",
    "sheet_url": null,
    "exists": false
  }
}
```

**Error Response** (400):

```json
{
  "success": false,
  "error": "Bad request",
  "message": "Invalid month-year format. Use format: 'July-2025'"
}
```

**Example**:

```bash
curl http://localhost:5000/api/v1/sheets/July-2025
```

---

### 5. Get Monthly Spending Statistics

**Endpoint**: `GET /api/v1/stats/{month-year}`

**Description**: Get spending statistics for a specific month.

**Parameters**:

- `month-year`: Month and year in format "July-2025"

**Success Response** (200):

```json
{
  "success": true,
  "data": {
    "month_year": "July-2025",
    "total_spend": 108138.52,
    "transaction_count": 45,
    "categories": {
      "Other": {
        "amount": 50168.52,
        "count": 15
      },
      "Cash Withdrawal": {
        "amount": 26040.0,
        "count": 8
      },
      "Subscription": {
        "amount": 25938.0,
        "count": 3
      },
      "Transportation": {
        "amount": 2845.48,
        "count": 7
      },
      "Shopping": {
        "amount": 1458.59,
        "count": 4
      },
      "Food & Dining": {
        "amount": 1052.0,
        "count": 6
      },
      "Utilities": {
        "amount": 213.0,
        "count": 1
      },
      "Investment": {
        "amount": 88.0,
        "count": 1
      }
    },
    "generated_at": "2025-07-16T10:30:00.000Z"
  }
}
```

**Response Fields**:

- `month_year`: The month and year in format "July-2025"
- `total_spend`: Total amount spent in the month
- `transaction_count`: Total number of transactions across all categories
- `categories`: Object containing category data with amount and transaction count per category
  - `amount`: Total amount spent in this category
  - `count`: Number of transactions in this category
- `generated_at`: Timestamp when the response was generated

**Error Responses**:

**400 Bad Request**:

```json
{
  "success": false,
  "error": "Bad request",
  "message": "Invalid month-year format. Use format: 'July-2025'"
}
```

**404 Not Found**:

```json
{
  "success": false,
  "error": "Sheet not found",
  "message": "No sheet found for June-2025"
}
```

**503 Service Unavailable**:

```json
{
  "success": false,
  "error": "Service unavailable",
  "message": "Google Sheets service is not available"
}
```

**Example**:

```bash
curl http://localhost:5000/api/v1/stats/July-2025
```

---

### 6. Get Transactions by Date

**Endpoint**: `GET /api/v1/transactions/{date}`

**Description**: Retrieve all transactions for a specific date.

**Parameters**:

- **Path Parameter**: `date` (string) - Date in format `YYYY-MM-DD` (e.g., `2025-09-05`)

**Headers**:

```
X-API-KEY: your-api-key-here
```

**Response**:

```json
{
  "success": true,
  "data": {
    "date": "2025-09-05",
    "transaction_count": 2,
    "transactions": [
      {
        "row_index": 3,
        "Date": "2025-09-05",
        "Transaction ID": "TXN123456",
        "Amount": "-50.00",
        "Type": "Food Order",
        "Friend Split": "25.00",
        "Notes": "Lunch with friends",
        "Account": "HDFC Credit Card ***1234"
      },
      {
        "row_index": 4,
        "Date": "2025-09-05",
        "Transaction ID": "TXN789012",
        "Amount": "-20.00",
        "Type": "Transport",
        "Friend Split": "0.00",
        "Notes": "Uber ride",
        "Account": "HDFC Debit Card ***5678"
      }
    ],
    "generated_at": "2025-09-05T14:30:00.000Z"
  },
  "message": "Retrieved 2 transactions for 2025-09-05"
}
```

**Error Responses**:

**400 Bad Request** (Invalid date format):

```json
{
  "success": false,
  "error": "Invalid date format. Use format: 'YYYY-MM-DD'",
  "message": "Bad request"
}
```

**Example**:

```bash
curl -H "X-API-KEY: your-api-key" \
     http://localhost:5000/api/v1/transactions/2025-09-05
```

---

### 7. Update Transaction Fields

**Endpoint**: `PATCH /api/v1/transactions`

**Description**: Update multiple fields in a specific transaction row.

**Headers**:

```
Content-Type: application/json
X-API-KEY: your-api-key-here
```

**Request Body**:

```json
{
  "sheet_name": "September-2025",
  "row_index": 3,
  "updates": {
    "Type": "Food Order",
    "Friend Split": "75.00",
    "Notes": "Updated notes for transaction"
  }
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "sheet_name": "September-2025",
    "row_index": 3,
    "updated_fields": {
      "Type": "Food Order",
      "Friend Split": "75.00",
      "Notes": "Updated notes for transaction"
    },
    "updated_at": "2025-09-05T14:35:00.000Z"
  },
  "message": "Transaction updated successfully in September-2025 at row 3"
}
```

**Error Responses**:

**400 Bad Request** (Missing required field):

```json
{
  "success": false,
  "error": "'sheet_name' field is required",
  "message": "Bad request"
}
```

**400 Bad Request** (Invalid field name):

```json
{
  "success": false,
  "error": "Invalid field name: 'InvalidField'. Must be one of: Date, Transaction ID, Amount, Type, Friend Split, Notes, Account",
  "message": "Bad request"
}
```

**400 Bad Request** (Invalid row index):

```json
{
  "success": false,
  "error": "Invalid row index. Row index must be >= 2 (data rows only)",
  "message": "Bad request"
}
```

**Example**:

```bash
curl -X PATCH \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: your-api-key" \
     -d '{"sheet_name": "September-2025", "row_index": 3, "updates": {"Type": "Food Order", "Notes": "Updated notes"}}' \
     http://localhost:5000/api/v1/transactions
```

---

### 8. Delete Transaction Row

**Endpoint**: `DELETE /api/v1/transactions`

**Description**: Delete a complete transaction row from the specified sheet.

**Headers**:

```
Content-Type: application/json
X-API-KEY: your-api-key-here
```

**Request Body**:

```json
{
  "sheet_name": "September-2025",
  "row_index": 3
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "sheet_name": "September-2025",
    "deleted_row_index": 3,
    "deleted_at": "2025-09-05T14:40:00.000Z"
  },
  "message": "Transaction deleted successfully from September-2025 at row 3"
}
```

**Error Responses**:

**400 Bad Request** (Missing required field):

```json
{
  "success": false,
  "error": "'sheet_name' field is required",
  "message": "Bad request"
}
```

**400 Bad Request** (Invalid row index):

```json
{
  "success": false,
  "error": "Invalid row index. Row index must be >= 2 (data rows only)",
  "message": "Bad request"
}
```

**500 Internal Server Error** (Deletion failed):

```json
{
  "success": false,
  "error": "Deletion failed",
  "message": "Failed to delete transaction from Google Sheets"
}
```

**Example**:

```bash
curl -X DELETE \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: your-api-key" \
     -d '{"sheet_name": "September-2025", "row_index": 3}' \
     http://localhost:5000/api/v1/transactions
```

---

## 📊 Caching Information

### Statistics Endpoints Caching

The statistics endpoints (`/api/v1/stats` and `/api/v1/stats/{month-year}`) implement caching for performance:

- **Cache TTL**: 50 minutes (3000 seconds)
- **Cache Key**: Based on sheet name (e.g., "July-2025")
- **Cache Hit Performance**: ~0-1ms response time
- **Cache Miss Performance**: ~2-3 seconds (Google Sheets API call)

### Cache Behavior

1. **First Request**: Calls Google Sheets API, caches result
2. **Subsequent Requests**: Returns cached data instantly
3. **Cache Expiry**: After 50 minutes, next request refreshes cache
4. **Error Handling**: If cache fails, falls back to direct API call

---

## 🚨 Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request format or parameters
- **404 Not Found**: Resource not found (sheet doesn't exist)
- **405 Method Not Allowed**: HTTP method not supported
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Google Sheets service unavailable

### Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error message"
}
```

---

## 🔧 Request/Response Examples

### JavaScript (Fetch API)

```javascript
// Log SMS transaction
async function logSMS(smsText, date, apiKey) {
  const response = await fetch("http://localhost:5000/api/v1/transactions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": apiKey,
    },
    body: JSON.stringify({
      text: smsText,
      date: date || new Date().toISOString(),
    }),
  });

  const data = await response.json();
  return data;
}

// Get spending statistics
async function getSpendingStats(apiKey, monthYear) {
  const url = monthYear
    ? `http://localhost:5000/api/v1/stats/${monthYear}`
    : "http://localhost:5000/api/v1/stats";

  const response = await fetch(url, {
    headers: {
      "X-API-KEY": apiKey,
    },
  });
  const data = await response.json();
  return data;
}
```

### Python (Requests)

```python
import requests
import json

# Log SMS transaction
def log_sms(sms_text, api_key, date=None):
    url = 'http://localhost:5000/api/v1/transactions'
    headers = {'X-API-KEY': api_key}
    payload = {'text': sms_text}
    if date:
        payload['date'] = date

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Get spending statistics
def get_spending_stats(api_key, month_year=None):
    headers = {'X-API-KEY': api_key}
    if month_year:
        url = f'http://localhost:5000/api/v1/stats/{month_year}'
    else:
        url = 'http://localhost:5000/api/v1/stats'

    response = requests.get(url, headers=headers)
    return response.json()
```

---

## 🧪 Testing Endpoints

### Using curl

```bash
# Test all endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/v1/parse-sms -H "Content-Type: application/json" -H "X-API-KEY: your-api-key-here" -d '{"text": "Test SMS"}'
curl -X POST http://localhost:5000/api/v1/transactions -H "Content-Type: application/json" -H "X-API-KEY: your-api-key-here" -d '{"text": "Test SMS", "date": "2025-07-14T10:30:00"}'
curl -H "X-API-KEY: your-api-key-here" http://localhost:5000/api/v1/sheets/July-2025
curl -H "X-API-KEY: your-api-key-here" http://localhost:5000/api/v1/stats/July-2025
```

### Using Python Test Script

```bash
# Run comprehensive tests
python run_tests.py

# Run simple tests
python simple_test.py
```

---

## 📈 Performance Considerations

### Response Times

- **Health Check**: ~1-5ms
- **SMS Parser Test**: ~10-50ms
- **SMS Logging**: ~1-3 seconds (Google Sheets write)
- **Statistics (First Call)**: ~2-3 seconds
- **Statistics (Cached)**: ~0-1ms

### Rate Limiting

Currently no rate limiting is implemented. For production use, consider:

- Adding rate limiting middleware
- Implementing request throttling
- Using Redis for distributed caching

### Optimization Tips

1. **Use caching**: Statistics endpoints benefit from caching
2. **Batch operations**: For multiple SMS, consider batch endpoint
3. **Monitor performance**: Use logs to track response times
4. **Optimize queries**: Google Sheets API calls are the bottleneck

---

## 🔒 Security Considerations

### Authentication

API key authentication is implemented using the `X-API-KEY` header for all API endpoints:

- **Current Implementation**: X-API-KEY header validation for `/api/v1/*` routes
- **Health Endpoint**: `/health` endpoint is publicly accessible
- **Environment Variable**: API key is configured via `API_KEY` environment variable
- **Error Handling**: Returns 403 Forbidden for missing/invalid keys

For additional security in production, consider:

- JWT token validation for user-based authentication
- Rate limiting per API key
- API key rotation mechanisms
- OAuth2 for user authentication

### Input Validation

- All inputs are validated
- JSON schema validation
- SQL injection prevention
- XSS protection

### Data Privacy

- No sensitive data logged
- Transaction data encrypted in transit
- Google Sheets access controlled via service account

---

## 📚 Related Documentation

- **Main Documentation**: `README.md`
- **SMS Parser**: `sms_parser/README.md`
- **Testing**: Use `run_tests.py`
- **Setup**: Follow setup instructions in `README.md`

---

## 🆘 Troubleshooting

### Common Issues

1. **503 Service Unavailable**: Check Google Sheets credentials
2. **400 Bad Request**: Validate request format
3. **404 Not Found**: Check if sheet exists for the month
4. **Slow Response**: First statistics call is slow, subsequent calls are cached

### Debug Steps

1. Check server logs
2. Verify Google Sheets service is running
3. Test individual endpoints with curl
4. Run comprehensive test suite

### Support

For issues:

1. Check endpoint documentation above
2. Run `python run_tests.py` for diagnostics
3. Check application logs in `logs/` directory
