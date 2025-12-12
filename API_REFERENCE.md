# API Reference

## Overview

The backend exposes RESTful endpoints for email operations and AI analysis.

**Base URL**: `http://localhost:8000`

---

## Email Endpoints

### List Emails
**GET** `/gmail/list`

Returns all emails from the mailbox.

**Response**:
```json
{
  "data": {
    "emails": [
      {
        "id": "msg_abc123",
        "gmail_id": "g_xyz789",
        "subject": "Your invoice for AWS Services #1",
        "from_email": "contact@amazon.com",
        "snippet": "This is a preview of the email...",
        "body": "Hi there, ...",
        "category": "Billing",
        "sentiment": "Neutral",
        "urgency": "Normal",
        "date": "2024-12-11T10:30:00Z",
        "isRead": false,
        "isStarred": false
      }
    ]
  }
}
```

---

### Fetch Emails
**GET** `/gmail/fetch`

Syncs emails from Gmail or loads sample data.

**Query Parameters**:
- `use_sample` (optional): `true` to use sample data, `false` to sync from Gmail

**Response**:
```json
{
  "data": {
    "message": "Fetched emails successfully"
  }
}
```

---

### Delete Emails
**POST** `/gmail/delete`

Deletes emails by Gmail ID.

**Request**:
```json
{
  "gmail_ids": ["g_id1", "g_id2"],
  "skip_remote": true
}
```

**Response**:
```json
{
  "data": {
    "deleted": 2
  }
}
```

---

### Move Emails
**POST** `/gmail/move`

Moves emails to a label.

**Request**:
```json
{
  "gmail_ids": ["g_id1", "g_id2"],
  "label_id": "INBOX",
  "skip_remote": true
}
```

**Response**:
```json
{
  "data": {
    "moved": true
  }
}
```

---

## Categorization Endpoint

### Categorize Email
**POST** `/categorize/email`

Analyzes and categorizes a single email.

**Request**:
```json
{
  "subject": "Q4 Goals Update",
  "body": "Hi team, please review the attached Q4 goals...",
  "gmail_id": "g_abc123",
  "from_email": "boss@company.com"
}
```

**Response**:
```json
{
  "data": {
    "email": {
      "gmail_id": "g_abc123",
      "subject": "Q4 Goals Update",
      "from_email": "boss@company.com",
      "category": "Work Update",
      "sentiment": "Neutral",
      "urgency": "High",
      "status": "keep"
    }
  }
}
```

---

## Assistant / Gemini Endpoints

### Legacy: GPT Reply
**POST** `/assistant/reply`

Generates a reply using OpenAI GPT.

**Request**:
```json
{
  "prompt": "Draft a response to a customer complaint about..."
}
```

**Response**:
```json
{
  "reply": "Dear Customer, thank you for reaching out..."
}
```

---

### Gemini: Summarize Email
**POST** `/assistant/gemini/summarize`

Summarizes email content into 3 bullet points.

**Request**:
```json
{
  "prompt": "Hi there, I hope this email finds you well. We need to discuss the Q4 goals and the AWS invoice discrepancies. Please review the attached documents by Friday. Best, Sender"
}
```

**Response**:
```json
{
  "reply": "• The sender is asking about Q4 goals.\n• An AWS invoice needs review.\n• Deadline is Friday."
}
```

---

### Gemini: Extract Action Items
**POST** `/assistant/gemini/actions`

Extracts tasks from email as a checklist.

**Request**:
```json
{
  "prompt": "Hi team, we need to: 1) Review the Q4 goals document, 2) Check the AWS invoice for discrepancies, 3) Schedule a meeting for Friday."
}
```

**Response**:
```json
{
  "reply": "- [ ] Review the Q4 goals document\n- [ ] Check the AWS invoice for discrepancies\n- [ ] Schedule a meeting for Friday"
}
```

---

### Gemini: Rewrite Draft
**POST** `/assistant/gemini/rewrite`

Rewrites email draft in specified tone.

**Request**:
```json
{
  "text": "hey check out the docs about q4 goals asap thx",
  "tone": "Professional"
}
```

**Response**:
```json
{
  "reply": "Dear Recipient, I would like to bring your attention to the Q4 goals documentation. Your review at your earliest convenience would be greatly appreciated. Sincerely, User"
}
```

**Supported Tones**:
- `Professional` - Formal, respectful
- `Friendly` - Casual, warm
- `Concise` - Short, direct

---

## Data Models

### EmailRecord
```python
{
  "id": int,                          # Database ID
  "gmail_id": str,                    # Gmail message ID
  "subject": str,                     # Email subject
  "snippet": str,                     # Preview text
  "body_text": str,                   # Full email body
  "from_email": str,                  # Sender email
  "category": str,                    # Category (see below)
  "sentiment": str,                   # Sentiment: Positive/Negative/Neutral
  "urgency": str,                     # Urgency: High/Normal
  "status": str,                      # Status: keep/deleted/archived
  "is_read": bool,                    # Read status
  "is_starred": bool,                 # Starred status
  "created_at": datetime,             # Created timestamp
  "updated_at": datetime              # Last updated timestamp
}
```

### Email Categories
- `Billing` - Invoices, payments, receipts
- `Account Info` - Login, security, account details
- `Work Update` - Meetings, projects, deadlines
- `Promotion` - Sales, discounts, offers
- `Spam` - Unwanted mail, phishing
- `Personal` - Friends, family, social

### Sentiment Values
- `Positive` - Positive/happy tone
- `Negative` - Negative/angry tone
- `Neutral` - Neutral/factual tone

### Urgency Levels
- `High` - Contains urgent keywords (asap, deadline, critical, etc.)
- `Normal` - Not urgent

---

## Error Handling

All endpoints return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Codes**:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing credentials)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error (internal issue)

---

## Rate Limiting

Gemini API has rate limits:
- **50 requests per minute** (free tier)
- **100,000 requests per day** (free tier)

Implement exponential backoff for production use.

---

## Authentication

Currently, endpoints are **unauthenticated** (local development).

For production, add:
- API key validation
- JWT tokens
- OAuth 2.0 integration

---

## Examples

### Complete Workflow

**1. Fetch emails**
```bash
curl -X GET http://localhost:8000/gmail/fetch
```

**2. Get email list**
```bash
curl -X GET http://localhost:8000/gmail/list
```

**3. Summarize first email**
```bash
curl -X POST http://localhost:8000/assistant/gemini/summarize \
  -H "Content-Type: application/json" \
  -d '{"prompt": "email body text here..."}'
```

**4. Extract actions**
```bash
curl -X POST http://localhost:8000/assistant/gemini/actions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "email body text here..."}'
```

**5. Rewrite as professional**
```bash
curl -X POST http://localhost:8000/assistant/gemini/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text": "draft text...", "tone": "Professional"}'
```

---

## Frontend Integration

The frontend uses a client abstraction layer that:
1. Routes to mock data in Demo Mode
2. Routes to real API in Live Mode
3. Handles errors gracefully

**Client Usage** (in `frontend/src/App.jsx`):
```javascript
const api = createClient(baseUrl, isDemoMode);

// GET request
const res = await api.get('/gmail/list');

// POST request
const res = await api.post('/assistant/gemini/summarize', { 
  prompt: "email text" 
});
```

---

## Testing Endpoints

### Using curl

```bash
# Test backend is running
curl http://localhost:8000/docs

# Get email list (JSON)
curl -H "Accept: application/json" http://localhost:8000/gmail/list

# Test Gemini summarize
curl -X POST http://localhost:8000/assistant/gemini/summarize \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test email content"}'
```

### Using Postman

1. Open Postman
2. Create new request
3. Set method to `POST`
4. Set URL to `http://localhost:8000/assistant/gemini/summarize`
5. Add JSON body: `{"prompt": "Test content"}`
6. Click Send

### Using Python

```python
import requests

# Summarize email
response = requests.post(
    'http://localhost:8000/assistant/gemini/summarize',
    json={'prompt': 'email content...'}
)
print(response.json())
```

---

## API Documentation UI

FastAPI provides interactive API docs at:

**Swagger UI**: `http://localhost:8000/docs`
**ReDoc**: `http://localhost:8000/redoc`

Browse all endpoints and test them interactively!

---

**Need help?** Check the main documentation or raise an issue.
