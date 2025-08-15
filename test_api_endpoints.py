#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints with various sample data and includes webhook functionality
"""

import requests
import json
import time
import os
import uuid
from typing import Dict, List, Any
from pathlib import Path
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import threading

# API Configuration
API_BASE_URL = "http://localhost:8000"
WEBHOOK_PORT = 8001

# Sample test data
SAMPLE_QUERIES = [
    {
        "file_id": "test_file_1",
        "age": 35,
        "gender": "male",
        "procedure": "knee surgery",
        "location": "Mumbai",
        "policy_duration_months": 12
    },
    {
        "file_id": "test_file_2",
        "age": 45,
        "gender": "female",
        "procedure": "lost luggage",
        "location": "Delhi",
        "policy_duration_months": 6
    },
    {
        "file_id": "test_file_3",
        "age": 28,
        "gender": "male",
        "procedure": "accident claim",
        "location": "Bangalore",
        "policy_duration_months": 24
    },
    {
        "file_id": "test_file_4",
        "age": 52,
        "gender": "female",
        "procedure": "hospitalization",
        "location": "Chennai",
        "policy_duration_months": 18
    },
    {
        "file_id": "test_file_5",
        "age": 31,
        "gender": "male",
        "procedure": "theft claim",
        "location": "Pune",
        "policy_duration_months": 9
    }
]

NATURAL_LANGUAGE_QUERIES = [
    "A 35-year-old male wants to claim for knee surgery in Mumbai after 12 months of policy",
    "45-year-old female lost her luggage during travel to Delhi, policy is 6 months old",
    "28-year-old male had an accident in Bangalore, policy duration is 24 months",
    "52-year-old female needs hospitalization in Chennai, policy is 18 months old",
    "31-year-old male had theft claim in Pune, policy is 9 months old"
]

# Webhook storage
webhook_events = []

# Webhook models
class WebhookEvent(BaseModel):
    event_type: str
    timestamp: float
    data: Dict[str, Any]
    endpoint: str
    status: str

# Webhook server
webhook_app = FastAPI(title="Webhook Receiver", version="1.0.0")

@webhook_app.post("/webhook/upload")
async def webhook_upload(data: Dict[str, Any]):
    """Webhook endpoint for upload events"""
    event = WebhookEvent(
        event_type="file_upload",
        timestamp=time.time(),
        data=data,
        endpoint="/upload/",
        status="received"
    )
    webhook_events.append(event)
    print(f"📤 Webhook received upload event: {data}")
    return {"status": "received", "event_id": len(webhook_events)}

@webhook_app.post("/webhook/query")
async def webhook_query(data: Dict[str, Any]):
    """Webhook endpoint for query events"""
    event = WebhookEvent(
        event_type="query",
        timestamp=time.time(),
        data=data,
        endpoint="/query/",
        status="received"
    )
    webhook_events.append(event)
    print(f"📤 Webhook received query event: {data}")
    return {"status": "received", "event_id": len(webhook_events)}

@webhook_app.post("/webhook/nl_query")
async def webhook_nl_query(data: Dict[str, Any]):
    """Webhook endpoint for natural language query events"""
    event = WebhookEvent(
        event_type="nl_query",
        timestamp=time.time(),
        data=data,
        endpoint="/nl_query/",
        status="received"
    )
    webhook_events.append(event)
    print(f"📤 Webhook received nl_query event: {data}")
    return {"status": "received", "event_id": len(webhook_events)}

@webhook_app.get("/webhook/events")
async def get_webhook_events():
    """Get all webhook events"""
    return {
        "total_events": len(webhook_events),
        "events": [event.dict() for event in webhook_events]
    }

@webhook_app.delete("/webhook/clear")
async def clear_webhook_events():
    """Clear all webhook events"""
    global webhook_events
    webhook_events = []
    return {"status": "cleared", "message": "All webhook events cleared"}

def start_webhook_server():
    """Start the webhook server in a separate thread"""
    uvicorn.run(webhook_app, host="0.0.0.0", port=WEBHOOK_PORT, log_level="info")

class APITester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.uploaded_files = {}
        
    def test_health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint"""
        print("\n🏥 Testing Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = {
                "endpoint": "/health",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Health check: {result['success']}")
            return result
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"endpoint": "/health", "success": False, "error": str(e)}

    def test_root_endpoint(self) -> Dict[str, Any]:
        """Test the root endpoint"""
        print("\n🏠 Testing Root Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            result = {
                "endpoint": "/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Root endpoint: {result['success']}")
            return result
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
            return {"endpoint": "/", "success": False, "error": str(e)}

    def test_upload_endpoint(self, file_path: str) -> Dict[str, Any]:
        """Test the upload endpoint with a file"""
        print(f"\n📤 Testing Upload Endpoint with {file_path}...")
        try:
            if not os.path.exists(file_path):
                return {
                    "endpoint": "/upload/",
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                response = self.session.post(f"{self.base_url}/upload/", files=files)
            
            result = {
                "endpoint": "/upload/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            
            if result["success"]:
                file_id = result["response"].get("file_id")
                self.uploaded_files[file_id] = file_path
                print(f"✅ Upload successful: {file_id}")
            else:
                print(f"❌ Upload failed: {result['response']}")
            
            return result
        except Exception as e:
            print(f"❌ Upload test failed: {e}")
            return {"endpoint": "/upload/", "success": False, "error": str(e)}

    def test_query_endpoint(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the query endpoint"""
        print(f"\n🔍 Testing Query Endpoint with: {query_data}")
        try:
            headers = {'Content-Type': 'application/json'}
            response = self.session.post(
                f"{self.base_url}/query/",
                json=query_data,
                headers=headers
            )
            
            result = {
                "endpoint": "/query/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text,
                "query_data": query_data
            }
            
            if result["success"]:
                print(f"✅ Query successful")
            else:
                print(f"❌ Query failed: {result['response']}")
            
            return result
        except Exception as e:
            print(f"❌ Query test failed: {e}")
            return {"endpoint": "/query/", "success": False, "error": str(e), "query_data": query_data}

    def test_nl_query_endpoint(self, file_id: str, query_text: str) -> Dict[str, Any]:
        """Test the natural language query endpoint"""
        print(f"\n🗣️ Testing NL Query Endpoint with: {query_text}")
        try:
            data = {
                "file_id": file_id,
                "query_text": query_text
            }
            
            headers = {'Content-Type': 'application/json'}
            response = self.session.post(
                f"{self.base_url}/nl_query/",
                json=data,
                headers=headers
            )
            
            result = {
                "endpoint": "/nl_query/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text,
                "query_data": data
            }
            
            if result["success"]:
                print(f"✅ NL Query successful")
            else:
                print(f"❌ NL Query failed: {result['response']}")
            
            return result
        except Exception as e:
            print(f"❌ NL Query test failed: {e}")
            return {"endpoint": "/nl_query/", "success": False, "error": str(e), "query_data": data}

    def test_with_webhooks(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test query endpoint with webhook notification"""
        print(f"\n🔗 Testing Query with Webhook: {query_data}")
        try:
            # Add webhook URL to query data
            webhook_data = {
                **query_data,
                "webhook_url": f"http://localhost:{WEBHOOK_PORT}/webhook/query"
            }
            
            headers = {'Content-Type': 'application/json'}
            response = self.session.post(
                f"{self.base_url}/query/",
                json=webhook_data,
                headers=headers
            )
            
            result = {
                "endpoint": "/query/ (with webhook)",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text,
                "query_data": webhook_data
            }
            
            if result["success"]:
                print(f"✅ Query with webhook successful")
            else:
                print(f"❌ Query with webhook failed: {result['response']}")
            
            return result
        except Exception as e:
            print(f"❌ Query with webhook test failed: {e}")
            return {"endpoint": "/query/ (with webhook)", "success": False, "error": str(e), "query_data": webhook_data}

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive API Testing...")
        
        results = {
            "health_check": self.test_health_check(),
            "root_endpoint": self.test_root_endpoint(),
            "uploads": [],
            "queries": [],
            "nl_queries": [],
            "webhook_tests": []
        }
        
        # Test uploads with different files
        test_files = [
            "documents/sample_policy.pdf",
            "documents/BAJHLIP23020V012223.pdf",
            "documents/CHOTGDP23004V012223.pdf"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                upload_result = self.test_upload_endpoint(file_path)
                results["uploads"].append(upload_result)
                
                # If upload successful, test queries with the file_id
                if upload_result["success"]:
                    file_id = upload_result["response"].get("file_id")
                    
                    # Test structured queries
                    for i, query_data in enumerate(SAMPLE_QUERIES[:3]):  # Test first 3 queries
                        query_data["file_id"] = file_id
                        query_result = self.test_query_endpoint(query_data)
                        results["queries"].append(query_result)
                    
                    # Test natural language queries
                    for i, nl_query in enumerate(NATURAL_LANGUAGE_QUERIES[:3]):  # Test first 3 NL queries
                        nl_result = self.test_nl_query_endpoint(file_id, nl_query)
                        results["nl_queries"].append(nl_result)
                    
                    # Test webhook functionality
                    webhook_query_data = SAMPLE_QUERIES[0].copy()
                    webhook_query_data["file_id"] = file_id
                    webhook_result = self.test_with_webhooks(webhook_query_data)
                    results["webhook_tests"].append(webhook_result)
                    
                    break  # Only test with first successful upload
        
        return results

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE API TEST REPORT")
        report.append("=" * 80)
        
        # Summary
        total_tests = 0
        passed_tests = 0
        
        # Health and root endpoints
        for test_name in ["health_check", "root_endpoint"]:
            if test_name in results:
                test_result = results[test_name]
                total_tests += 1
                if test_result.get("success", False):
                    passed_tests += 1
                status = "✅ PASS" if test_result.get("success", False) else "❌ FAIL"
                report.append(f"{status} {test_name}: {test_result.get('status_code', 'N/A')}")
        
        # Upload tests
        report.append(f"\n📤 UPLOAD TESTS ({len(results.get('uploads', []))} tests):")
        for i, upload_result in enumerate(results.get("uploads", [])):
            total_tests += 1
            if upload_result.get("success", False):
                passed_tests += 1
            status = "✅ PASS" if upload_result.get("success", False) else "❌ FAIL"
            report.append(f"{status} Upload {i+1}: {upload_result.get('status_code', 'N/A')}")
        
        # Query tests
        report.append(f"\n🔍 QUERY TESTS ({len(results.get('queries', []))} tests):")
        for i, query_result in enumerate(results.get("queries", [])):
            total_tests += 1
            if query_result.get("success", False):
                passed_tests += 1
            status = "✅ PASS" if query_result.get("success", False) else "❌ FAIL"
            report.append(f"{status} Query {i+1}: {query_result.get('status_code', 'N/A')}")
        
        # NL Query tests
        report.append(f"\n🗣️ NATURAL LANGUAGE QUERY TESTS ({len(results.get('nl_queries', []))} tests):")
        for i, nl_result in enumerate(results.get("nl_queries", [])):
            total_tests += 1
            if nl_result.get("success", False):
                passed_tests += 1
            status = "✅ PASS" if nl_result.get("success", False) else "❌ FAIL"
            report.append(f"{status} NL Query {i+1}: {nl_result.get('status_code', 'N/A')}")
        
        # Webhook tests
        report.append(f"\n🔗 WEBHOOK TESTS ({len(results.get('webhook_tests', []))} tests):")
        for i, webhook_result in enumerate(results.get("webhook_tests", [])):
            total_tests += 1
            if webhook_result.get("success", False):
                passed_tests += 1
            status = "✅ PASS" if webhook_result.get("success", False) else "❌ FAIL"
            report.append(f"{status} Webhook {i+1}: {webhook_result.get('status_code', 'N/A')}")
        
        # Final summary
        report.append("\n" + "=" * 80)
        report.append(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main function to run all tests"""
    print("🚀 Starting API Testing Suite...")
    
    # Start webhook server in background
    print(f"🔗 Starting webhook server on port {WEBHOOK_PORT}...")
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()
    
    # Wait for webhook server to start
    time.sleep(3)
    
    # Create tester and run tests
    tester = APITester()
    results = tester.run_comprehensive_tests()
    
    # Generate and print report
    report = tester.generate_test_report(results)
    print(report)
    
    # Save detailed results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"api_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Print webhook events if any
    try:
        webhook_response = requests.get(f"http://localhost:{WEBHOOK_PORT}/webhook/events")
        if webhook_response.status_code == 200:
            webhook_data = webhook_response.json()
            print(f"\n📤 Webhook Events: {webhook_data['total_events']} events received")
    except:
        print("\n📤 Webhook Events: Could not retrieve webhook events")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()

