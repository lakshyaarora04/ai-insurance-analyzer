#!/usr/bin/env python3
"""
Test script for the FastAPI insurance claim evaluation endpoint
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 TESTING FASTAPI INSURANCE CLAIM EVALUATION")
    print("=" * 60)
    
    # Test 1: Cataract surgery with 24 months (should be approved)
    test_case_1 = {
        "age": 40,
        "gender": "male",
        "procedure": "cataract surgery",
        "location": "Pune",
        "policy_duration_months": 24
    }
    
    # Test 2: Cataract surgery with 12 months (should be rejected due to waiting period)
    test_case_2 = {
        "age": 40,
        "gender": "male",
        "procedure": "cataract surgery",
        "location": "Pune",
        "policy_duration_months": 12
    }
    
    # Test 3: Different procedure
    test_case_3 = {
        "age": 35,
        "gender": "female",
        "procedure": "appendectomy",
        "location": "Mumbai",
        "policy_duration_months": 6
    }
    
    test_cases = [
        ("Cataract Surgery (24 months policy)", test_case_1),
        ("Cataract Surgery (12 months policy)", test_case_2),
        ("Appendectomy (6 months policy)", test_case_3)
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n🔍 TESTING: {test_name}")
        print("-" * 40)
        print(f"Query: {json.dumps(test_data, indent=2)}")
        
        try:
            response = requests.post(
                f"{base_url}/query/",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"🎯 Decision: {result.get('decision', 'N/A').upper()}")
                print(f"💰 Amount: ₹{result.get('amount', 0)}")
                print(f"📝 Justification: {result.get('justification', 'N/A')}")
                print(f"📊 Retrieved Chunks: {result.get('retrieved_chunks', 'N/A')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
            print("   Run: python run_server.py")
            break
        except requests.exceptions.Timeout:
            print("❌ Timeout: Request took too long (LLM processing can be slow)")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
        time.sleep(1)  # Small delay between requests
    
    print("=" * 60)
    print("✅ API Testing Complete")

if __name__ == "__main__":
    test_api() 