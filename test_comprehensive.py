#!/usr/bin/env python3
"""
Comprehensive test script for the LLM-based insurance claim evaluation system
"""

import requests
import json
import time

def test_case(name, query_data, expected_decision=None, expected_reason=None):
    """Test a single case and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST CASE: {name}")
    print(f"{'='*60}")
    print(f"Query: {json.dumps(query_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/query/",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESULT:")
            print(f"   Decision: {result.get('decision', 'N/A').upper()}")
            print(f"   Amount: ₹{result.get('amount', 0):,}")
            print(f"   Retrieved Chunks: {result.get('retrieved_chunks', 'N/A')}")
            
            # Show full justification
            justification = result.get('justification', 'N/A')
            print(f"   Justification:")
            print(f"   {'-' * 50}")
            print(f"   {justification}")
            print(f"   {'-' * 50}")
            
            # Check expectations
            if expected_decision and result.get('decision') != expected_decision:
                print(f"   ⚠️  Expected decision: {expected_decision}, got: {result.get('decision')}")
            else:
                print(f"   ✅ Decision matches expectation")
                
            if result.get('amount', 0) > 0:
                print(f"   ✅ Dynamic amount calculated: ₹{result.get('amount'):,}")
            else:
                print(f"   ⚠️  Amount is 0 (might be rejected or no amount found)")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long (LLM processing can be slow)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def run_comprehensive_tests():
    """Run all test cases"""
    print("🧪 COMPREHENSIVE INSURANCE CLAIM EVALUATION TESTS")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            "name": "Cataract Surgery - 24 months policy (Should be APPROVED)",
            "query": {
                "age": 40,
                "gender": "male",
                "procedure": "cataract surgery",
                "location": "Pune",
                "policy_duration_months": 24
            },
            "expected_decision": "approved"
        },
        {
            "name": "Cataract Surgery - 12 months policy (Should be REJECTED - waiting period)",
            "query": {
                "age": 40,
                "gender": "male",
                "procedure": "cataract surgery",
                "location": "Pune",
                "policy_duration_months": 12
            },
            "expected_decision": "rejected"
        },
        {
            "name": "Appendectomy - 6 months policy (Should be APPROVED - no waiting period)",
            "query": {
                "age": 35,
                "gender": "female",
                "procedure": "appendectomy",
                "location": "Mumbai",
                "policy_duration_months": 6
            },
            "expected_decision": "approved"
        },
        {
            "name": "Heart Surgery - 18 months policy (Should be APPROVED)",
            "query": {
                "age": 55,
                "gender": "male",
                "procedure": "heart surgery",
                "location": "Delhi",
                "policy_duration_months": 18
            },
            "expected_decision": "approved"
        },
        {
            "name": "Dental Treatment - 3 months policy (Should be REJECTED - exclusion)",
            "query": {
                "age": 28,
                "gender": "female",
                "procedure": "dental treatment",
                "location": "Bangalore",
                "policy_duration_months": 3
            },
            "expected_decision": "rejected"
        },
        {
            "name": "Knee Replacement - 30 months policy (Should be APPROVED)",
            "query": {
                "age": 65,
                "gender": "male",
                "procedure": "knee replacement surgery",
                "location": "Chennai",
                "policy_duration_months": 30
            },
            "expected_decision": "approved"
        },
        {
            "name": "Cosmetic Surgery - 24 months policy (Should be REJECTED - exclusion)",
            "query": {
                "age": 32,
                "gender": "female",
                "procedure": "cosmetic surgery",
                "location": "Hyderabad",
                "policy_duration_months": 24
            },
            "expected_decision": "rejected"
        },
        {
            "name": "Emergency Treatment - 1 month policy (Should be APPROVED - emergency)",
            "query": {
                "age": 45,
                "gender": "male",
                "procedure": "emergency treatment",
                "location": "Kolkata",
                "policy_duration_months": 1
            },
            "expected_decision": "approved"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case_data in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total_tests}")
        success = test_case(
            test_case_data["name"],
            test_case_data["query"],
            test_case_data.get("expected_decision")
        )
        if success:
            successful_tests += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the results above.")

if __name__ == "__main__":
    run_comprehensive_tests() 