#!/usr/bin/env python3
"""
Webhook Demonstration Script
Shows webhook functionality working with sample data
"""

import requests
import json
import time
import os

# Configuration
WEBHOOK_BASE_URL = "http://localhost:8001"

def demo_webhook_server():
    """Demonstrate webhook server functionality"""
    print("🚀 Webhook Server Demonstration")
    print("=" * 50)
    
    # Test 1: Check webhook server health
    print("\n1️⃣ Testing Webhook Server Health...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Webhook server is healthy: {health['status']}")
            print(f"   Service: {health['service']}")
            print(f"   Total events: {health['total_events']}")
        else:
            print(f"❌ Webhook server health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to webhook server: {e}")
        return
    
    # Test 2: Send sample webhook events
    print("\n2️⃣ Sending Sample Webhook Events...")
    
    sample_events = [
        {
            "event_type": "file_upload",
            "data": {
                "file_id": "demo_file_001",
                "filename": "sample_policy.pdf",
                "num_chunks": 15,
                "file_size": 2048,
                "file_type": ".pdf"
            }
        },
        {
            "event_type": "query",
            "data": {
                "file_id": "demo_file_001",
                "query": {
                    "age": 35,
                    "gender": "male",
                    "procedure": "knee surgery",
                    "location": "Mumbai",
                    "policy_duration_months": 12
                },
                "result": {
                    "decision": "approved",
                    "confidence": 0.85,
                    "reasoning": "Based on policy terms, knee surgery is covered under this insurance policy."
                },
                "num_chunks_retrieved": 8
            }
        },
        {
            "event_type": "nl_query",
            "data": {
                "file_id": "demo_file_001",
                "original_query": "A 35-year-old male wants to claim for knee surgery in Mumbai after 12 months of policy",
                "structured_query": {
                    "age": 35,
                    "gender": "male",
                    "procedure": "knee surgery",
                    "location": "Mumbai",
                    "policy_duration_months": 12
                },
                "result": {
                    "decision": "approved",
                    "confidence": 0.85,
                    "reasoning": "Natural language query processed successfully. Policy covers knee surgery."
                }
            }
        },
        {
            "event_type": "query",
            "data": {
                "file_id": "demo_file_002",
                "query": {
                    "age": 45,
                    "gender": "female",
                    "procedure": "lost luggage",
                    "location": "Delhi",
                    "policy_duration_months": 6
                },
                "result": {
                    "decision": "approved",
                    "confidence": 0.92,
                    "reasoning": "Lost luggage is covered under travel insurance policy."
                },
                "num_chunks_retrieved": 5
            }
        }
    ]
    
    for i, event in enumerate(sample_events):
        print(f"\n📤 Sending event {i+1}: {event['event_type']}")
        try:
            response = requests.post(
                f"{WEBHOOK_BASE_URL}/webhook/{event['event_type']}",
                json=event
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Event processed successfully")
                print(f"   Event ID: {result['event_id']}")
                print(f"   Status: {result['status']}")
                if 'processing_result' in result:
                    proc_result = result['processing_result']
                    print(f"   Action: {proc_result.get('action', 'N/A')}")
                    print(f"   Message: {proc_result.get('message', 'N/A')}")
            else:
                print(f"❌ Event failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error sending event: {e}")
    
    # Test 3: Check webhook statistics
    print("\n3️⃣ Checking Webhook Statistics...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Webhook Statistics:")
            print(f"   Total events: {stats['total_events']}")
            print(f"   Events by type: {stats['events_by_type']}")
            print(f"   Last event time: {stats.get('last_event_time', 'N/A')}")
            print(f"   Uptime: {stats.get('uptime', 0):.1f} seconds")
        else:
            print(f"❌ Failed to get webhook stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting webhook stats: {e}")
    
    # Test 4: Get recent events
    print("\n4️⃣ Recent Webhook Events...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/webhook/events")
        if response.status_code == 200:
            events_data = response.json()
            print(f"✅ Recent Events (showing last {len(events_data['events'])} events):")
            
            for i, event in enumerate(events_data['events']):
                print(f"\n   Event {i+1}:")
                print(f"     Type: {event['event_type']}")
                print(f"     Timestamp: {event['timestamp']}")
                print(f"     Endpoint: {event['endpoint']}")
                print(f"     Status: {event['status']}")
                print(f"     Processed: {event['processed']}")
                
                # Show some data details
                data = event['data']
                if event['event_type'] == 'file_upload':
                    print(f"     File: {data.get('filename', 'N/A')} (ID: {data.get('file_id', 'N/A')})")
                elif event['event_type'] == 'query':
                    query = data.get('query', {})
                    print(f"     Query: {query.get('procedure', 'N/A')} for {query.get('age', 'N/A')}-year-old {query.get('gender', 'N/A')}")
                elif event['event_type'] == 'nl_query':
                    print(f"     NL Query: {data.get('original_query', 'N/A')[:50]}...")
        else:
            print(f"❌ Failed to get webhook events: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting webhook events: {e}")
    
    # Test 5: Test webhook server root endpoint
    print("\n5️⃣ Webhook Server Information...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Webhook Server Info:")
            print(f"   Message: {info['message']}")
            print(f"   Available endpoints:")
            for endpoint, path in info['endpoints'].items():
                print(f"     {endpoint}: {path}")
        else:
            print(f"❌ Failed to get server info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting server info: {e}")

def demo_api_endpoints():
    """Demonstrate API endpoints with sample data"""
    print("\n" + "=" * 50)
    print("🌐 API Endpoints Demonstration")
    print("=" * 50)
    
    print("\n📋 Available API Endpoints:")
    print("   GET  /health - Health check")
    print("   GET  / - Root endpoint")
    print("   POST /upload/ - Upload file")
    print("   POST /query/ - Structured query")
    print("   POST /nl_query/ - Natural language query")
    print("   GET  /files/ - List uploaded files")
    print("   DELETE /files/{file_id} - Delete file")
    
    print("\n📋 Available Webhook Endpoints:")
    print("   POST /webhook/upload - Receive upload events")
    print("   POST /webhook/query - Receive query events")
    print("   POST /webhook/nl_query - Receive NL query events")
    print("   GET  /webhook/events - Get all events")
    print("   GET  /webhook/stats - Get statistics")
    print("   DELETE /webhook/clear - Clear events")
    
    print("\n📋 Sample Test Data:")
    print("   Files: documents/sample_policy.pdf")
    print("   Queries: Knee surgery, Lost luggage, Accident claims")
    print("   NL Queries: Natural language descriptions of claims")

def main():
    """Main function"""
    print("🚀 Webhook and API Demonstration")
    print("=" * 60)
    
    # Check if webhook server is running
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Webhook server is running")
            demo_webhook_server()
        else:
            print("❌ Webhook server is not responding properly")
    except Exception as e:
        print(f"❌ Webhook server is not running: {e}")
        print("💡 To start the webhook server, run: python webhook_server.py")
    
    # Show API endpoint information
    demo_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Demonstration completed!")
    print("📚 For more information, see API_DOCUMENTATION.md")
    print("🧪 To run comprehensive tests, use: python test_api_endpoints.py")
    print("🔗 Webhook server: http://localhost:8001")
    print("🌐 API server: http://localhost:8000")
    print("=" * 60)

if __name__ == "__main__":
    main()

