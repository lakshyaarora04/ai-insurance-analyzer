#!/usr/bin/env python3
"""
Test Public Webhook URL
Verifies that the public webhook URL is working correctly
"""

import requests
import json
import time

# Public webhook URL
PUBLIC_URL = "https://21bfed7abe7d.ngrok-free.app"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{PUBLIC_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Total Events: {data.get('total_events')}")
            print(f"   Uptime: {data.get('uptime', 0):.1f} seconds")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_webhook_query():
    """Test webhook query endpoint"""
    print("\n🔍 Testing Webhook Query Endpoint...")
    
    test_data = {
        "event_type": "query",
        "data": {
            "file_id": "test_public_123",
            "query": {
                "procedure": "knee surgery",
                "age": 35,
                "gender": "male",
                "location": "Mumbai",
                "policy_duration_months": 12
            },
            "result": {
                "decision": "approved",
                "confidence": 0.85,
                "reasoning": "Based on policy terms, knee surgery is covered"
            },
            "num_chunks_retrieved": 8
        }
    }
    
    try:
        response = requests.post(
            f"{PUBLIC_URL}/webhook/query",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook query test passed!")
            print(f"   Event ID: {result.get('event_id')}")
            print(f"   Status: {result.get('status')}")
            
            if 'processing_result' in result:
                proc_result = result['processing_result']
                print(f"   Action: {proc_result.get('action')}")
                print(f"   Message: {proc_result.get('message')}")
            
            return True
        else:
            print(f"❌ Webhook query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook query error: {e}")
        return False

def test_webhook_upload():
    """Test webhook upload endpoint"""
    print("\n📤 Testing Webhook Upload Endpoint...")
    
    test_data = {
        "event_type": "file_upload",
        "data": {
            "file_id": "upload_test_123",
            "filename": "sample_policy.pdf",
            "num_chunks": 15,
            "file_size": 2048,
            "file_type": ".pdf"
        }
    }
    
    try:
        response = requests.post(
            f"{PUBLIC_URL}/webhook/upload",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook upload test passed!")
            print(f"   Event ID: {result.get('event_id')}")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Webhook upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook upload error: {e}")
        return False

def test_webhook_nl_query():
    """Test webhook natural language query endpoint"""
    print("\n🗣️ Testing Webhook NL Query Endpoint...")
    
    test_data = {
        "event_type": "nl_query",
        "data": {
            "file_id": "nl_test_123",
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
                "reasoning": "Natural language query processed successfully"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{PUBLIC_URL}/webhook/nl_query",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook NL query test passed!")
            print(f"   Event ID: {result.get('event_id')}")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Webhook NL query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook NL query error: {e}")
        return False

def test_webhook_stats():
    """Test webhook statistics endpoint"""
    print("\n📊 Testing Webhook Statistics Endpoint...")
    
    try:
        response = requests.get(f"{PUBLIC_URL}/webhook/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Webhook stats test passed!")
            print(f"   Total Events: {stats.get('total_events')}")
            print(f"   Events by Type: {stats.get('events_by_type')}")
            print(f"   Last Event Time: {stats.get('last_event_time')}")
            print(f"   Uptime: {stats.get('uptime', 0):.1f} seconds")
            return True
        else:
            print(f"❌ Webhook stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook stats error: {e}")
        return False

def test_webhook_events():
    """Test webhook events endpoint"""
    print("\n📋 Testing Webhook Events Endpoint...")
    
    try:
        response = requests.get(f"{PUBLIC_URL}/webhook/events", timeout=10)
        
        if response.status_code == 200:
            events_data = response.json()
            print("✅ Webhook events test passed!")
            print(f"   Total Events: {events_data.get('total_events')}")
            print(f"   Recent Events: {len(events_data.get('events', []))}")
            return True
        else:
            print(f"❌ Webhook events failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook events error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Public Webhook URL")
    print("=" * 50)
    print(f"🌐 URL: {PUBLIC_URL}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Webhook Query", test_webhook_query),
        ("Webhook Upload", test_webhook_upload),
        ("Webhook NL Query", test_webhook_nl_query),
        ("Webhook Stats", test_webhook_stats),
        ("Webhook Events", test_webhook_events)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your public webhook URL is working perfectly!")
        print(f"🌐 Public URL: {PUBLIC_URL}")
        print("🔗 Ready to receive webhook events from anywhere!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("🔧 Please check the webhook server and network connectivity")
    
    print("\n📋 Quick Test Commands:")
    print(f"curl -X GET '{PUBLIC_URL}/health'")
    print(f"curl -X POST '{PUBLIC_URL}/webhook/query' -H 'Content-Type: application/json' -d '{{\"event_type\": \"query\", \"data\": {{\"file_id\": \"test\"}}}}'")
    print(f"curl -X GET '{PUBLIC_URL}/webhook/stats'")

if __name__ == "__main__":
    main()

