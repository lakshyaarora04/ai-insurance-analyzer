#!/usr/bin/env python3
"""
Simple Webhook Test Script
Demonstrates webhook functionality with the API endpoints
"""

import requests
import json
import time
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
WEBHOOK_BASE_URL = "http://localhost:8001"

def test_webhook_functionality():
    """Test webhook functionality with the API"""
    print("🚀 Testing Webhook Functionality...")
    
    # Test 1: Upload file with webhook
    print("\n📤 Test 1: Upload file with webhook")
    test_file = "documents/sample_policy.pdf"
    
    if os.path.exists(test_file):
        with open(test_file, 'rb') as f:
            files = {'file': ('sample_policy.pdf', f, 'application/pdf')}
            data = {
                'webhook_url': f"{WEBHOOK_BASE_URL}/webhook/upload",
                'webhook_secret': 'test_secret_123'
            }
            
            response = requests.post(f"{API_BASE_URL}/upload/", files=files, data=data)
            print(f"Upload response: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                file_id = result.get('file_id')
                print(f"✅ File uploaded successfully: {file_id}")
                
                # Test 2: Query with webhook
                print("\n🔍 Test 2: Query with webhook")
                query_data = {
                    "file_id": file_id,
                    "age": 35,
                    "gender": "male",
                    "procedure": "knee surgery",
                    "location": "Mumbai",
                    "policy_duration_months": 12,
                    "webhook_url": f"{WEBHOOK_BASE_URL}/webhook/query",
                    "webhook_secret": "test_secret_123"
                }
                
                response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
                print(f"Query response: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Query processed successfully")
                    print(f"Decision: {result.get('decision', 'Unknown')}")
                
                # Test 3: Natural language query with webhook
                print("\n🗣️ Test 3: Natural language query with webhook")
                nl_query_data = {
                    "file_id": file_id,
                    "query_text": "A 45-year-old female lost her luggage during travel to Delhi, policy is 6 months old",
                    "webhook_url": f"{WEBHOOK_BASE_URL}/webhook/nl_query",
                    "webhook_secret": "test_secret_123"
                }
                
                response = requests.post(f"{API_BASE_URL}/nl_query/", json=nl_query_data)
                print(f"NL Query response: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ NL Query processed successfully")
                    print(f"Decision: {result.get('decision', 'Unknown')}")
            else:
                print(f"❌ Upload failed: {response.text}")
    else:
        print(f"❌ Test file not found: {test_file}")
    
    # Wait a moment for webhooks to be processed
    time.sleep(2)
    
    # Check webhook events
    print("\n📊 Checking webhook events...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/events")
        if response.status_code == 200:
            events = response.json()
            print(f"Total events received: {events['total_events']}")
            print(f"Events by type: {events['stats']['events_by_type']}")
            
            if events['events']:
                print("\nLast few events:")
                for event in events['events']:
                    print(f"  - {event['event_type']}: {event['data'].get('file_id', 'N/A')}")
        else:
            print(f"❌ Failed to get webhook events: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking webhook events: {e}")

def test_webhook_server_directly():
    """Test webhook server directly"""
    print("\n🔗 Testing Webhook Server Directly...")
    
    # Test webhook server health
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Webhook server healthy: {health['status']}")
        else:
            print(f"❌ Webhook server unhealthy: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to webhook server: {e}")
        return
    
    # Test direct webhook calls
    test_events = [
        {
            "event_type": "file_upload",
            "data": {
                "file_id": "test_123",
                "filename": "test.pdf",
                "num_chunks": 10,
                "file_size": 1024
            }
        },
        {
            "event_type": "query",
            "data": {
                "file_id": "test_123",
                "query": {"procedure": "test", "age": 30},
                "result": {"decision": "approved"},
                "num_chunks_retrieved": 5
            }
        },
        {
            "event_type": "nl_query",
            "data": {
                "file_id": "test_123",
                "original_query": "Test natural language query",
                "structured_query": {"procedure": "test"},
                "result": {"decision": "approved"}
            }
        }
    ]
    
    for i, event in enumerate(test_events):
        print(f"\n📤 Sending test event {i+1}: {event['event_type']}")
        try:
            response = requests.post(
                f"{WEBHOOK_BASE_URL}/webhook/{event['event_type']}",
                json=event
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Event processed: {result['status']}")
            else:
                print(f"❌ Event failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending event: {e}")

def main():
    """Main function"""
    print("🚀 Starting Webhook Testing...")
    
    # Test webhook server directly first
    test_webhook_server_directly()
    
    # Test webhook functionality with API
    test_webhook_functionality()
    
    print("\n✅ Webhook testing completed!")

if __name__ == "__main__":
    main()

