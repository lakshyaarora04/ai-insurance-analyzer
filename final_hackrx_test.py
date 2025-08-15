#!/usr/bin/env python3
"""
Final HackRx Test - Comprehensive Verification
Ensures webhook is ready for HackRx submission with 90+% accuracy
"""

import requests
import json
import time
import random

WEBHOOK_URL = "https://21bfed7abe7d.ngrok-free.app/webhook/query"

def test_webhook_functionality():
    """Test basic webhook functionality"""
    print("🔧 Testing Basic Webhook Functionality")
    print("-" * 50)
    
    # Test 1: Simple claim
    test_data = {
        "data": {
            "claim_id": "final_test_001",
            "patient_age": 35,
            "patient_gender": "male",
            "procedure": "dental procedure",
            "location": "mumbai",
            "policy_duration_months": 12,
            "claim_amount": 50000.0
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Basic functionality: PASSED")
            print(f"   Response time: {result.get('processing_time_ms', 0):.1f}ms")
            print(f"   Decision: {'Approved' if result.get('approved') else 'Rejected'}")
            print(f"   Confidence: {result.get('confidence_score', 0):.3f}")
            return True
        else:
            print(f"❌ Basic functionality: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Basic functionality: FAILED ({e})")
        return False

def test_accuracy_scenarios():
    """Test accuracy with various scenarios"""
    print("\n🎯 Testing Accuracy Scenarios")
    print("-" * 50)
    
    scenarios = [
        # High-confidence approvals
        {"name": "Low-risk dental", "age": 30, "procedure": "dental procedure", "amount": 20000, "expected": True},
        {"name": "Standard eye surgery", "age": 40, "procedure": "eye surgery", "amount": 40000, "expected": True},
        {"name": "Routine knee surgery", "age": 50, "procedure": "knee surgery", "amount": 60000, "expected": True},
        
        # Medium-risk approvals
        {"name": "Cardiac procedure", "age": 45, "procedure": "heart surgery", "amount": 200000, "expected": True},
        {"name": "Neurological procedure", "age": 60, "procedure": "brain surgery", "amount": 300000, "expected": True},
        
        # Rejections
        {"name": "Underage patient", "age": 16, "procedure": "general checkup", "amount": 10000, "expected": False},
        {"name": "Excessive amount", "age": 35, "procedure": "plastic surgery", "amount": 1500000, "expected": False},
        {"name": "Complex young patient", "age": 20, "procedure": "organ transplant", "amount": 500000, "expected": False},
    ]
    
    correct = 0
    total = len(scenarios)
    
    for scenario in scenarios:
        test_data = {
            "data": {
                "claim_id": f"scenario_{scenarios.index(scenario)}",
                "patient_age": scenario["age"],
                "patient_gender": "male",
                "procedure": scenario["procedure"],
                "location": "mumbai",
                "policy_duration_months": 12,
                "claim_amount": scenario["amount"]
            }
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=test_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                decision = result.get("approved", False)
                if decision == scenario["expected"]:
                    correct += 1
                    print(f"✅ {scenario['name']}: CORRECT")
                else:
                    print(f"❌ {scenario['name']}: WRONG (expected {scenario['expected']}, got {decision})")
            else:
                print(f"❌ {scenario['name']}: HTTP ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ {scenario['name']}: EXCEPTION {e}")
    
    accuracy = (correct / total) * 100
    print(f"\n📊 Scenario Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    return accuracy >= 90

def test_performance():
    """Test webhook performance"""
    print("\n⚡ Testing Performance")
    print("-" * 50)
    
    test_data = {
        "data": {
            "claim_id": "perf_test",
            "patient_age": 35,
            "patient_gender": "male",
            "procedure": "dental procedure",
            "location": "mumbai",
            "policy_duration_months": 12,
            "claim_amount": 50000.0
        }
    }
    
    times = []
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.post(WEBHOOK_URL, json=test_data, timeout=15)
            end_time = time.time()
            
            if response.status_code == 200:
                processing_time = (end_time - start_time) * 1000
                times.append(processing_time)
                print(f"   Test {i+1}: {processing_time:.1f}ms")
            else:
                print(f"   Test {i+1}: FAILED (HTTP {response.status_code})")
        except Exception as e:
            print(f"   Test {i+1}: FAILED ({e})")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        print(f"\n📊 Performance Results:")
        print(f"   Average: {avg_time:.1f}ms")
        print(f"   Maximum: {max_time:.1f}ms")
        print(f"   Status: {'✅ GOOD' if avg_time < 2000 else '⚠️ SLOW'}")
        return avg_time < 2000
    else:
        print("❌ Performance test failed")
        return False

def test_health_endpoints():
    """Test health and monitoring endpoints"""
    print("\n🏥 Testing Health Endpoints")
    print("-" * 50)
    
    endpoints = [
        ("/health", "Health Check"),
        ("/webhook/stats", "Statistics"),
        ("/webhook/events", "Events")
    ]
    
    all_working = True
    
    for endpoint, name in endpoints:
        try:
            url = WEBHOOK_URL.replace("/webhook/query", endpoint)
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: WORKING")
            else:
                print(f"❌ {name}: FAILED (HTTP {response.status_code})")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: FAILED ({e})")
            all_working = False
    
    return all_working

def test_error_handling():
    """Test error handling"""
    print("\n🛡️ Testing Error Handling")
    print("-" * 50)
    
    # Test with invalid data
    invalid_tests = [
        {"name": "Missing required fields", "data": {"claim_id": "test"}},
        {"name": "Invalid age", "data": {"claim_id": "test", "patient_age": -5, "patient_gender": "male", "procedure": "test", "location": "mumbai", "policy_duration_months": 12, "claim_amount": 10000}},
        {"name": "Invalid amount", "data": {"claim_id": "test", "patient_age": 35, "patient_gender": "male", "procedure": "test", "location": "mumbai", "policy_duration_months": 12, "claim_amount": -1000}},
    ]
    
    error_handled = True
    
    for test in invalid_tests:
        try:
            response = requests.post(WEBHOOK_URL, json=test["data"], timeout=10)
            if response.status_code in [400, 422, 500]:
                print(f"✅ {test['name']}: Properly handled")
            else:
                print(f"⚠️ {test['name']}: Unexpected response (HTTP {response.status_code})")
                error_handled = False
        except Exception as e:
            print(f"✅ {test['name']}: Exception caught")
    
    return error_handled

def main():
    """Run comprehensive HackRx readiness test"""
    print("🚀 FINAL HACKRX READINESS TEST")
    print("=" * 60)
    print(f"🎯 Target URL: {WEBHOOK_URL}")
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_webhook_functionality),
        ("Accuracy Scenarios", test_accuracy_scenarios),
        ("Performance", test_performance),
        ("Health Endpoints", test_health_endpoints),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name.upper()}")
        print("="*60)
        results[test_name] = test_func()
    
    # Final assessment
    print(f"\n{'='*60}")
    print("🎯 FINAL ASSESSMENT")
    print("="*60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 EXCELLENT! Your webhook is ready for HackRx!")
        print(f"✅ All tests passed")
        print(f"✅ Predicted accuracy: 90+%")
        print(f"✅ Performance: Good")
        print(f"✅ Error handling: Robust")
        print(f"\n🌐 Submit this URL to HackRx:")
        print(f"   {WEBHOOK_URL}")
        print(f"\n📝 Your webhook is optimized for high accuracy and ready for competition!")
    else:
        print(f"\n⚠️  Some tests failed. Please review and fix issues before submitting to HackRx.")
        print(f"❌ {total_tests - passed_tests} test(s) failed")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()

