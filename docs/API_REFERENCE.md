# 📚 API Reference Documentation

## Overview

The LLM Document Query System provides a comprehensive API for document analysis, insurance claim evaluation, and webhook integration. This document provides detailed information about all available endpoints, request/response formats, and usage examples.

## Base URL

- **Local Development**: `http://localhost:8001`
- **Production**: `https://your-domain.com`
- **ngrok Tunnel**: `https://your-ngrok-url.ngrok-free.app`

## Authentication

Currently, the API does not require authentication. However, for production deployments, consider implementing:

- API Key authentication
- JWT tokens
- OAuth 2.0

## Content Type

All requests should use:
```
Content-Type: application/json
```

## Response Format

All responses follow this standard format:

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🔍 Core Endpoints

### Health Check

#### `GET /health`

Check the health status of the webhook server.

**Request:**
```bash
curl -X GET "http://localhost:8001/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": "2h 15m 30s",
  "memory_usage": "45.2 MB"
}
```

**Status Codes:**
- `200 OK`: Server is healthy
- `503 Service Unavailable`: Server is unhealthy

---

## 🔗 Webhook Endpoints

### Main Query Endpoint

#### `POST /webhook/query`

The main endpoint that handles both document Q&A and insurance claim evaluation requests. The system automatically detects the request type based on the payload structure.

**Request Headers:**
```
Content-Type: application/json
User-Agent: Your-App/1.0
```

#### Document Q&A Request

**Request Body:**
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is covered under this policy?",
    "What are the claim procedures?",
    "Is dental treatment covered?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    {
      "question": "What is covered under this policy?",
      "answer": "Based on the policy document, the following treatments are covered: hospitalization expenses, pre and post-hospitalization expenses, day care procedures, and ambulance charges. The policy provides coverage for both medical and surgical treatments.",
      "confidence": 0.92,
      "source": "document_analysis",
      "relevant_sections": ["Coverage Details", "Policy Terms"]
    },
    {
      "question": "What are the claim procedures?",
      "answer": "To file a claim, you need to submit the following documents: 1) Duly filled claim form, 2) Medical certificates, 3) Hospital bills and receipts, 4) Discharge summary, 5) Investigation reports. Claims should be submitted within 30 days of discharge.",
      "confidence": 0.88,
      "source": "document_analysis",
      "relevant_sections": ["Claim Process", "Required Documents"]
    }
  ],
  "document_url": "https://example.com/document.pdf",
  "total_questions": 2,
  "processing_time_ms": 750,
  "document_type": "insurance_policy"
}
```

#### Insurance Claim Request

**Request Body:**
```json
{
  "data": {
    "claim_id": "claim_001",
    "patient_age": 35,
    "patient_gender": "male",
    "procedure": "dental procedure",
    "location": "mumbai",
    "policy_duration_months": 12,
    "claim_amount": 50000.0
  }
}
```

**Response:**
```json
{
  "claim_id": "claim_001",
  "approved": true,
  "approved_amount": 45000.0,
  "confidence_score": 0.85,
  "reasoning": "Claim approved based on the following factors: Patient age (35) is within acceptable range, dental procedures are covered under the policy, location (Mumbai) is in the covered network, policy duration (12 months) meets minimum requirements. Claim amount is reasonable for the procedure type.",
  "processing_time_ms": 650,
  "risk_factors": ["high_amount"],
  "policy_compliance": "compliant",
  "waiting_period_satisfied": true,
  "coverage_details": {
    "procedure_covered": true,
    "location_covered": true,
    "amount_within_limits": true
  }
}
```

**Status Codes:**
- `200 OK`: Request processed successfully
- `400 Bad Request`: Invalid request format
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

### Webhook Management Endpoints

#### `GET /webhook/stats`

Get webhook statistics and performance metrics.

**Request:**
```bash
curl -X GET "http://localhost:8001/webhook/stats"
```

**Response:**
```json
{
  "total_events": 150,
  "successful_events": 145,
  "failed_events": 5,
  "success_rate": 0.967,
  "average_response_time_ms": 750,
  "last_event_time": "2024-01-15T10:30:00Z",
  "event_types": {
    "document_qa": 80,
    "insurance_claim": 70
  },
  "performance_metrics": {
    "min_response_time": 100,
    "max_response_time": 800,
    "p95_response_time": 780,
    "requests_per_minute": 12.5
  }
}
```

#### `GET /webhook/events`

Get recent webhook events (last 100 events).

**Request:**
```bash
curl -X GET "http://localhost:8001/webhook/events"
```

**Response:**
```json
{
  "events": [
    {
      "id": "event_001",
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "document_qa",
      "status": "success",
      "processing_time_ms": 750,
      "request_data": {
        "documents": "https://example.com/policy.pdf",
        "questions_count": 2
      },
      "response_data": {
        "answers_count": 2,
        "average_confidence": 0.90
      }
    },
    {
      "id": "event_002",
      "timestamp": "2024-01-15T10:29:00Z",
      "type": "insurance_claim",
      "status": "success",
      "processing_time_ms": 650,
      "request_data": {
        "claim_id": "claim_001",
        "patient_age": 35
      },
      "response_data": {
        "approved": true,
        "confidence_score": 0.85
      }
    }
  ],
  "total_events": 100,
  "page": 1,
  "per_page": 100
}
```

#### `DELETE /webhook/clear`

Clear all webhook events and reset statistics.

**Request:**
```bash
curl -X DELETE "http://localhost:8001/webhook/clear"
```

**Response:**
```json
{
  "message": "All webhook events cleared successfully",
  "cleared_events": 150,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 📊 Data Models

### InsuranceClaimRequest

```json
{
  "claim_id": "string (required)",
  "patient_age": "integer (required, 0-120)",
  "patient_gender": "string (required, 'male'|'female'|'other')",
  "procedure": "string (required)",
  "location": "string (required)",
  "policy_duration_months": "integer (required, 1-120)",
  "claim_amount": "float (required, >0)"
}
```

### InsuranceClaimResponse

```json
{
  "claim_id": "string",
  "approved": "boolean",
  "approved_amount": "float",
  "confidence_score": "float (0.0-1.0)",
  "reasoning": "string",
  "processing_time_ms": "integer",
  "risk_factors": ["array of strings"],
  "policy_compliance": "string ('compliant'|'non_compliant')",
  "waiting_period_satisfied": "boolean",
  "coverage_details": {
    "procedure_covered": "boolean",
    "location_covered": "boolean",
    "amount_within_limits": "boolean"
  }
}
```

### DocumentQARequest

```json
{
  "documents": "string (URL, required)",
  "questions": ["array of strings (required, min 1)"]
}
```

### DocumentQAResponse

```json
{
  "answers": [
    {
      "question": "string",
      "answer": "string",
      "confidence": "float (0.0-1.0)",
      "source": "string",
      "relevant_sections": ["array of strings"]
    }
  ],
  "document_url": "string",
  "total_questions": "integer",
  "processing_time_ms": "integer",
  "document_type": "string"
}
```

---

## 🔧 Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INVALID_DOCUMENT_URL` | 400 | Document URL is invalid or inaccessible |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Example Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "patient_age": "Age must be between 0 and 120",
      "claim_amount": "Claim amount must be greater than 0"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🚀 Usage Examples

### Python Examples

#### Document Q&A Request

```python
import requests
import json

url = "http://localhost:8001/webhook/query"
payload = {
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is covered under this policy?",
        "What are the claim procedures?"
    ]
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Processing time: {result['processing_time_ms']}ms")
for answer in result['answers']:
    print(f"Q: {answer['question']}")
    print(f"A: {answer['answer']}")
    print(f"Confidence: {answer['confidence']}")
    print("---")
```

#### Insurance Claim Request

```python
import requests

url = "http://localhost:8001/webhook/query"
payload = {
    "data": {
        "claim_id": "claim_001",
        "patient_age": 35,
        "patient_gender": "male",
        "procedure": "dental procedure",
        "location": "mumbai",
        "policy_duration_months": 12,
        "claim_amount": 50000.0
    }
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Claim ID: {result['claim_id']}")
print(f"Approved: {result['approved']}")
print(f"Approved Amount: {result['approved_amount']}")
print(f"Confidence: {result['confidence_score']}")
print(f"Reasoning: {result['reasoning']}")
```

### cURL Examples

#### Health Check

```bash
curl -X GET "http://localhost:8001/health" \
  -H "Content-Type: application/json"
```

#### Document Q&A

```bash
curl -X POST "http://localhost:8001/webhook/query" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": [
      "What is covered under this policy?",
      "What are the claim procedures?"
    ]
  }'
```

#### Insurance Claim

```bash
curl -X POST "http://localhost:8001/webhook/query" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "claim_id": "claim_001",
      "patient_age": 35,
      "patient_gender": "male",
      "procedure": "dental procedure",
      "location": "mumbai",
      "policy_duration_months": 12,
      "claim_amount": 50000.0
    }
  }'
```

#### Get Statistics

```bash
curl -X GET "http://localhost:8001/webhook/stats" \
  -H "Content-Type: application/json"
```

---

## 📈 Rate Limiting

Currently, the API does not implement rate limiting. However, for production deployments, consider implementing:

- **Rate Limits**: 100 requests per minute per IP
- **Burst Limits**: 10 requests per second
- **Rate Limit Headers**: Include remaining requests in response headers

### Rate Limit Headers (Future Implementation)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

---

## 🔒 Security Considerations

### Input Validation

- All inputs are validated using Pydantic models
- URL validation for document links
- Type checking for all fields
- Range validation for numeric values

### Output Sanitization

- HTML entities are escaped in responses
- Sensitive data is not logged
- Error messages don't expose internal details

### Best Practices

1. **Use HTTPS** in production
2. **Validate all inputs** on the client side
3. **Handle errors gracefully**
4. **Implement proper logging**
5. **Monitor API usage**

---

## 📞 Support

For API support and questions:

- **Documentation**: This file and README.md
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions
- **Email**: your.email@example.com

---

## 📝 Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- Document Q&A functionality
- Insurance claim evaluation
- Webhook management endpoints
- Comprehensive error handling
