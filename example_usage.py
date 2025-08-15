#!/usr/bin/env python3
"""
Example Usage Script
Demonstrates how to use the API with webhook functionality
"""

import requests
import json
import time
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
WEBHOOK_BASE_URL = "http://localhost:8001"

def example_without_webhooks():
    """Example usage without webhooks"""
    print("🌐 Example: API Usage Without Webhooks")
    print("=" * 50)
    
    # This would work when the API server is running
    print("📋 Steps:")
    print("1. Upload a document")
    print("2. Get file_id from response")
    print("3. Submit queries using file_id")
    print("4. Process results")
    
    print("\n📝 Code Example:")
    print("""
# Upload file
with open('documents/sample_policy.pdf', 'rb') as f:
    files = {'file': ('sample_policy.pdf', f, 'application/pdf')}
    response = requests.post(f"{API_BASE_URL}/upload/", files=files)
    file_id = response.json()['file_id']

# Submit structured query
query_data = {
    "file_id": file_id,
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12
}
response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
result = response.json()
print(f"Decision: {result['decision']}")

# Submit natural language query
nl_data = {
    "file_id": file_id,
    "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai"
}
response = requests.post(f"{API_BASE_URL}/nl_query/", json=nl_data)
result = response.json()
print(f"Decision: {result['decision']}")
    """)

def example_with_webhooks():
    """Example usage with webhooks"""
    print("\n🔗 Example: API Usage With Webhooks")
    print("=" * 50)
    
    print("📋 Steps:")
    print("1. Start webhook server (python webhook_server.py)")
    print("2. Upload document with webhook_url")
    print("3. Submit queries with webhook notifications")
    print("4. Monitor webhook events")
    
    print("\n📝 Code Example:")
    print("""
# Upload file with webhook
with open('documents/sample_policy.pdf', 'rb') as f:
    files = {'file': ('sample_policy.pdf', f, 'application/pdf')}
    data = {
        'webhook_url': f"{WEBHOOK_BASE_URL}/webhook/upload",
        'webhook_secret': 'your_secret_123'
    }
    response = requests.post(f"{API_BASE_URL}/upload/", files=files, data=data)
    file_id = response.json()['file_id']

# Submit query with webhook
query_data = {
    "file_id": file_id,
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12,
    "webhook_url": f"{WEBHOOK_BASE_URL}/webhook/query",
    "webhook_secret": "your_secret_123"
}
response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
result = response.json()

# Check webhook events
response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/events")
events = response.json()
print(f"Total webhook events: {events['total_events']}")
    """)

def example_webhook_monitoring():
    """Example of webhook monitoring"""
    print("\n📊 Example: Webhook Monitoring")
    print("=" * 50)
    
    print("📋 Webhook Monitoring Endpoints:")
    print("- GET /webhook/events - Get all events")
    print("- GET /webhook/stats - Get statistics")
    print("- DELETE /webhook/clear - Clear events")
    
    print("\n📝 Monitoring Code Example:")
    print("""
# Get webhook statistics
response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/stats")
stats = response.json()
print(f"Total events: {stats['total_events']}")
print(f"Events by type: {stats['events_by_type']}")
print(f"Uptime: {stats.get('uptime', 0):.1f} seconds")

# Get recent events
response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/events")
events = response.json()
for event in events['events']:
    print(f"Event: {event['event_type']} at {event['timestamp']}")
    print(f"  Data: {event['data']}")

# Clear all events
response = requests.delete(f"{WEBHOOK_BASE_URL}/webhook/clear")
print("All events cleared")
    """)

def example_error_handling():
    """Example of error handling"""
    print("\n⚠️ Example: Error Handling")
    print("=" * 50)
    
    print("📋 Common Error Scenarios:")
    print("1. Invalid file_id")
    print("2. Unsupported file type")
    print("3. Missing required fields")
    print("4. Webhook server unavailable")
    
    print("\n📝 Error Handling Code Example:")
    print("""
try:
    # Try to upload file
    with open('invalid_file.txt', 'rb') as f:
        files = {'file': ('invalid_file.txt', f, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload/", files=files)
        
    if response.status_code != 200:
        error = response.json()
        print(f"Upload failed: {error['detail']}")
        
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")

try:
    # Try to submit query with invalid file_id
    query_data = {
        "file_id": "invalid_id",
        "procedure": "test"
    }
    response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
    
    if response.status_code != 200:
        error = response.json()
        print(f"Query failed: {error['detail']}")
        
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
    """)

def example_curl_commands():
    """Example cURL commands"""
    print("\n🔄 Example: cURL Commands")
    print("=" * 50)
    
    print("📋 cURL Examples:")
    print("""
# Upload file
curl -X POST "http://localhost:8000/upload/" \\
  -F "file=@documents/sample_policy.pdf" \\
  -F "webhook_url=http://localhost:8001/webhook/upload"

# Submit structured query
curl -X POST "http://localhost:8000/query/" \\
  -H "Content-Type: application/json" \\
  -d '{
    "file_id": "abc123",
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12,
    "webhook_url": "http://localhost:8001/webhook/query"
  }'

# Submit natural language query
curl -X POST "http://localhost:8000/nl_query/" \\
  -H "Content-Type: application/json" \\
  -d '{
    "file_id": "abc123",
    "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai"
  }'

# Get webhook statistics
curl -X GET "http://localhost:8001/webhook/stats"

# Get webhook events
curl -X GET "http://localhost:8001/webhook/events"
    """)

def main():
    """Main function"""
    print("🚀 API Usage Examples")
    print("=" * 60)
    
    # Show different usage examples
    example_without_webhooks()
    example_with_webhooks()
    example_webhook_monitoring()
    example_error_handling()
    example_curl_commands()
    
    print("\n" + "=" * 60)
    print("✅ Usage examples completed!")
    print("📚 For more details, see API_DOCUMENTATION.md")
    print("🧪 To test the examples, run: python test_webhooks.py")
    print("🔗 Webhook server: http://localhost:8001")
    print("🌐 API server: http://localhost:8000")
    print("=" * 60)

if __name__ == "__main__":
    main()

