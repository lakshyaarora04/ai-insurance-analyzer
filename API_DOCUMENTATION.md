# API Documentation

## Overview

This API provides endpoints for insurance claim evaluation using LLM reasoning. It supports file uploads, structured queries, natural language queries, and webhook notifications.

## Base URL

- **API Server**: `http://localhost:8000`
- **Webhook Server**: `http://localhost:8001`

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the API server.

**Response:**
```json
{
  "status": "healthy",
  "system": "LLM Insurance Claim Evaluator",
  "uploaded_files_count": 2,
  "endpoints": {
    "upload": "/upload/",
    "query": "/query/",
    "nl_query": "/nl_query/",
    "files": "/files/",
    "health": "/health"
  }
}
```

### 2. Root Endpoint

**GET** `/`

Get basic information about the API.

**Response:**
```json
{
  "message": "LLM Insurance Claim Evaluation System is running",
  "docs": "/docs",
  "endpoints": {
    "query": "/query/",
    "health": "/"
  }
}
```

### 3. File Upload

**POST** `/upload/`

Upload a document for processing. Supports PDF, DOCX, TXT, and HTML files.

**Parameters:**
- `file` (required): The file to upload
- `webhook_url` (optional): URL to send webhook notifications
- `webhook_secret` (optional): Secret for webhook authentication

**Request Example:**
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_policy.pdf" \
  -F "webhook_url=http://localhost:8001/webhook/upload" \
  -F "webhook_secret=your_secret"
```

**Response:**
```json
{
  "file_id": "abc123def456",
  "num_chunks": 15,
  "filename": "sample_policy.pdf"
}
```

### 4. Structured Query

**POST** `/query/`

Submit a structured query for claim evaluation.

**Request Body:**
```json
{
  "file_id": "abc123def456",
  "age": 35,
  "gender": "male",
  "procedure": "knee surgery",
  "location": "Mumbai",
  "policy_duration_months": 12,
  "webhook_url": "http://localhost:8001/webhook/query",
  "webhook_secret": "your_secret"
}
```

**Response:**
```json
{
  "decision": "approved",
  "confidence": 0.85,
  "reasoning": "Based on policy terms, knee surgery is covered...",
  "file_id": "abc123def456",
  "query": {
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery"
  }
}
```

### 5. Natural Language Query

**POST** `/nl_query/`

Submit a natural language query for claim evaluation.

**Request Body:**
```json
{
  "file_id": "abc123def456",
  "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai after 12 months of policy",
  "webhook_url": "http://localhost:8001/webhook/nl_query",
  "webhook_secret": "your_secret"
}
```

**Response:**
```json
{
  "decision": "approved",
  "confidence": 0.85,
  "reasoning": "Based on policy terms, knee surgery is covered...",
  "structured_query": {
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12
  }
}
```

### 6. List Uploaded Files

**GET** `/files/`

List all uploaded files with their metadata.

**Response:**
```json
{
  "files": [
    {
      "file_id": "abc123def456",
      "filename": "sample_policy.pdf",
      "num_chunks": 15,
      "uploaded_at": "timestamp_placeholder"
    }
  ]
}
```

### 7. Delete Uploaded File

**DELETE** `/files/{file_id}`

Delete an uploaded file and its associated data.

**Response:**
```json
{
  "message": "File abc123def456 deleted successfully"
}
```

## Webhook Functionality

### Webhook Server Endpoints

The webhook server runs on port 8001 and provides the following endpoints:

#### Webhook Event Receivers

**POST** `/webhook/upload`
- Receives file upload events
- Processes upload metadata

**POST** `/webhook/query`
- Receives structured query events
- Processes query results

**POST** `/webhook/nl_query`
- Receives natural language query events
- Processes NL query results

#### Webhook Management

**GET** `/webhook/events`
- Get all received webhook events
- Returns last 10 events with statistics

**GET** `/webhook/stats`
- Get webhook server statistics
- Shows event counts and uptime

**DELETE** `/webhook/clear`
- Clear all webhook events
- Reset statistics

### Webhook Payload Format

All webhook events follow this format:

```json
{
  "event_type": "file_upload|query|nl_query",
  "timestamp": 1640995200.0,
  "data": {
    // Event-specific data
  }
}
```

### Webhook Headers

Webhook requests include these headers:
- `Content-Type: application/json`
- `X-Event-Type: {event_type}`
- `X-Timestamp: {timestamp}`
- `X-Webhook-Secret: {secret}` (if provided)

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (file not found)
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message describing the issue"
}
```

## Testing

### Running the Tests

1. **Start the API server:**
```bash
python run_server.py
```

2. **Start the webhook server:**
```bash
python webhook_server.py
```

3. **Run comprehensive API tests:**
```bash
python test_api_endpoints.py
```

4. **Run webhook tests:**
```bash
python test_webhooks.py
```

### Sample Test Data

The test scripts include various sample queries:

**Structured Queries:**
- Knee surgery for 35-year-old male in Mumbai
- Lost luggage for 45-year-old female in Delhi
- Accident claim for 28-year-old male in Bangalore
- Hospitalization for 52-year-old female in Chennai
- Theft claim for 31-year-old male in Pune

**Natural Language Queries:**
- "A 35-year-old male wants to claim for knee surgery in Mumbai after 12 months of policy"
- "45-year-old female lost her luggage during travel to Delhi, policy is 6 months old"
- "28-year-old male had an accident in Bangalore, policy duration is 24 months"

### Test Files

The system includes several test PDF files:
- `documents/sample_policy.pdf` - Basic insurance policy
- `documents/BAJHLIP23020V012223.pdf` - Bajaj Allianz policy
- `documents/CHOTGDP23004V012223.pdf` - Cholamandalam policy

## Usage Examples

### Python Client Example

```python
import requests

# Upload a file
with open('sample_policy.pdf', 'rb') as f:
    files = {'file': ('sample_policy.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/upload/', files=files)
    file_id = response.json()['file_id']

# Submit a structured query
query_data = {
    "file_id": file_id,
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12
}
response = requests.post('http://localhost:8000/query/', json=query_data)
result = response.json()
print(f"Decision: {result['decision']}")

# Submit a natural language query
nl_data = {
    "file_id": file_id,
    "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai"
}
response = requests.post('http://localhost:8000/nl_query/', json=nl_data)
result = response.json()
print(f"Decision: {result['decision']}")
```

### cURL Examples

```bash
# Upload file
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@sample_policy.pdf"

# Structured query
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc123",
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12
  }'

# Natural language query
curl -X POST "http://localhost:8000/nl_query/" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc123",
    "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai"
  }'
```

## Configuration

### Environment Variables

- `API_PORT`: Port for the main API server (default: 8000)
- `WEBHOOK_PORT`: Port for the webhook server (default: 8001)
- `WEBHOOK_TIMEOUT`: Timeout for webhook requests (default: 10 seconds)

### Dependencies

The API requires the following Python packages:
- fastapi
- uvicorn
- requests
- pydantic
- numpy
- scikit-learn
- PyPDF2
- python-docx

## Security Considerations

1. **Webhook Security**: Use webhook secrets for authentication
2. **File Validation**: Only PDF, DOCX, TXT, and HTML files are accepted
3. **Input Validation**: All inputs are validated using Pydantic models
4. **Error Handling**: Comprehensive error handling with detailed messages

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Monitoring

The webhook server provides monitoring endpoints:
- `/health` - Server health status
- `/webhook/stats` - Event statistics
- `/webhook/events` - Recent events

## Troubleshooting

### Common Issues

1. **File upload fails**: Check file format and size
2. **Query fails**: Ensure file_id is valid and file was uploaded
3. **Webhook not received**: Check webhook URL and network connectivity
4. **Server not starting**: Check port availability and dependencies

### Debug Mode

Enable debug logging by setting the log level to DEBUG in the server configuration.

## Support

For issues and questions, check the test files and documentation in the project repository.

