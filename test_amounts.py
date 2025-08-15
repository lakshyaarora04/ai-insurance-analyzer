#!/usr/bin/env python3
"""
Test script to demonstrate dynamic amount calculation
"""

import requests
import json

def test_amount_calculation():
    print("💰 TESTING DYNAMIC AMOUNT CALCULATION")
    print("=" * 60)
    
    # Test different procedures to see different amounts
    test_cases = [
        {
            "name": "Cataract Surgery",
            "query": {
                "age": 40,
                "gender": "male",
                "procedure": "cataract surgery",
                "location": "Pune",
                "policy_duration_months": 24
            }
        },
        {
            "name": "Heart Surgery",
            "query": {
                "age": 55,
                "gender": "male",
                "procedure": "heart surgery",
                "location": "Delhi",
                "policy_duration_months": 18
            }
        },
        {
            "name": "Knee Replacement",
            "query": {
                "age": 65,
                "gender": "male",
                "procedure": "knee replacement surgery",
                "location": "Chennai",
                "policy_duration_months": 30
            }
        },
        {
            "name": "Appendectomy",
            "query": {
                "age": 35,
                "gender": "female",
                "procedure": "appendectomy",
                "location": "Mumbai",
                "policy_duration_months": 6
            }
        },
        {
            "name": "Emergency Treatment",
            "query": {
                "age": 45,
                "gender": "male",
                "procedure": "emergency treatment",
                "location": "Kolkata",
                "policy_duration_months": 1
            }
        }
    ]
    
    print("📋 Testing different procedures and their calculated amounts:\n")
    
    for test_case in test_cases:
        print(f"🔍 {test_case['name']}")
        print(f"   Procedure: {test_case['query']['procedure']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/query/",
                json=test_case['query'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                decision = result.get('decision', 'N/A').upper()
                amount = result.get('amount', 0)
                
                print(f"   Decision: {decision}")
                print(f"   Amount: ₹{amount:,}")
                
                if amount > 0:
                    print(f"   ✅ Dynamic amount calculated successfully")
                else:
                    print(f"   ⚠️  No amount calculated (likely rejected)")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("✅ Amount calculation test complete!")

if __name__ == "__main__":
    test_amount_calculation() 