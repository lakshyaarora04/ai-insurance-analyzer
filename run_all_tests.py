#!/usr/bin/env python3
"""
Run All Tests Script
Comprehensive testing of all API endpoints with webhook functionality
"""

import subprocess
import time
import sys
import os
import requests
import json
from pathlib import Path

def check_server_running(url, name):
    """Check if a server is running"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is running at {url}")
            return True
        else:
            print(f"❌ {name} is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ {name} is not running at {url}")
        return False

def start_server(script_name, port, name):
    """Start a server in the background"""
    print(f"🚀 Starting {name} on port {port}...")
    try:
        process = subprocess.Popen([
            sys.executable, script_name
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ {name} started successfully")
            return process
        else:
            print(f"❌ Failed to start {name}")
            return None
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def run_test_script(script_name, description):
    """Run a test script"""
    print(f"\n🧪 Running {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
            print(result.stdout)
        else:
            print("❌ Test failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running test: {e}")

def test_webhook_functionality():
    """Test webhook functionality directly"""
    print("\n🔗 Testing Webhook Functionality...")
    
    # Test webhook server endpoints
    webhook_url = "http://localhost:8001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{webhook_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Webhook server health: {health['status']}")
        else:
            print(f"❌ Webhook server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to webhook server: {e}")
        return
    
    # Test webhook events
    test_events = [
        {
            "event_type": "file_upload",
            "data": {
                "file_id": "test_webhook_123",
                "filename": "test_webhook.pdf",
                "num_chunks": 5,
                "file_size": 512
            }
        },
        {
            "event_type": "query",
            "data": {
                "file_id": "test_webhook_123",
                "query": {"procedure": "test procedure", "age": 30},
                "result": {"decision": "test_approved"},
                "num_chunks_retrieved": 3
            }
        }
    ]
    
    for i, event in enumerate(test_events):
        print(f"\n📤 Sending test webhook event {i+1}: {event['event_type']}")
        try:
            response = requests.post(
                f"{webhook_url}/webhook/{event['event_type']}",
                json=event
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhook event processed: {result['status']}")
            else:
                print(f"❌ Webhook event failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending webhook event: {e}")
    
    # Check webhook statistics
    try:
        response = requests.get(f"{webhook_url}/webhook/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Webhook Statistics:")
            print(f"  Total events: {stats['total_events']}")
            print(f"  Events by type: {stats['events_by_type']}")
        else:
            print(f"❌ Failed to get webhook stats")
    except Exception as e:
        print(f"❌ Error getting webhook stats: {e}")

def main():
    """Main function to run all tests"""
    print("🚀 Starting Comprehensive API Testing Suite...")
    print("=" * 80)
    
    # Check if servers are already running
    api_running = check_server_running("http://localhost:8000", "API Server")
    webhook_running = check_server_running("http://localhost:8001", "Webhook Server")
    
    processes = []
    
    # Start API server if not running
    if not api_running:
        api_process = start_server("run_server.py", 8000, "API Server")
        if api_process:
            processes.append(api_process)
    
    # Start webhook server if not running
    if not webhook_running:
        webhook_process = start_server("webhook_server.py", 8001, "Webhook Server")
        if webhook_process:
            processes.append(webhook_process)
    
    # Wait for servers to be ready
    print("\n⏳ Waiting for servers to be ready...")
    time.sleep(5)
    
    # Test webhook functionality
    test_webhook_functionality()
    
    # Run comprehensive API tests
    run_test_script("test_api_endpoints.py", "Comprehensive API Endpoint Tests")
    
    # Run webhook tests
    run_test_script("test_webhooks.py", "Webhook Functionality Tests")
    
    # Generate test report
    print("\n📊 Generating Test Report...")
    print("=" * 60)
    
    # Check final webhook status
    try:
        response = requests.get("http://localhost:8001/webhook/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Final Webhook Statistics:")
            print(f"  Total events: {stats['total_events']}")
            print(f"  Events by type: {stats['events_by_type']}")
            print(f"  Uptime: {stats.get('uptime', 0):.1f} seconds")
    except Exception as e:
        print(f"Could not get final webhook stats: {e}")
    
    # Check API health
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health = response.json()
            print(f"\nAPI Health Status:")
            print(f"  Status: {health['status']}")
            print(f"  Uploaded files: {health.get('uploaded_files_count', 0)}")
    except Exception as e:
        print(f"Could not get API health: {e}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("📄 Check the generated test result files for detailed information.")
    print("🔗 Webhook server is running at: http://localhost:8001")
    print("🌐 API server is running at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("=" * 80)
    
    # Clean up processes if we started them
    if processes:
        print("\n🛑 Stopping test servers...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ Test servers stopped")

if __name__ == "__main__":
    main()

