#!/usr/bin/env python3
"""
Test script to demonstrate improved justifications for both approved and rejected cases
"""

import requests
import json

def test_justifications():
    print("📝 TESTING IMPROVED JUSTIFICATIONS")
    print("=" * 80)
    
    # Test cases focused on justifications
    test_cases = [
        {
            "name": "APPROVED CASE: Cataract Surgery (24 months)",
            "query": {
                "age": 40,
                "gender": "male",
                "procedure": "cataract surgery",
                "location": "Pune",
                "policy_duration_months": 24
            },
            "expected": "approved"
        },
        {
            "name": "REJECTED CASE: Cataract Surgery (12 months - waiting period)",
            "query": {
                "age": 40,
                "gender": "male",
                "procedure": "cataract surgery",
                "location": "Pune",
                "policy_duration_months": 12
            },
            "expected": "rejected"
        },
        {
            "name": "REJECTED CASE: Cosmetic Surgery (exclusion)",
            "query": {
                "age": 32,
                "gender": "female",
                "procedure": "cosmetic surgery",
                "location": "Hyderabad",
                "policy_duration_months": 24
            },
            "expected": "rejected"
        },
        {
            "name": "REJECTED CASE: Dental Treatment (exclusion)",
            "query": {
                "age": 28,
                "gender": "female",
                "procedure": "dental treatment",
                "location": "Bangalore",
                "policy_duration_months": 3
            },
            "expected": "rejected"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"🧪 TEST {i}: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Query: {json.dumps(test_case['query'], indent=2)}")
        
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
                justification = result.get('justification', 'N/A')
                
                print(f"\n📊 RESULT:")
                print(f"   Decision: {decision}")
                print(f"   Amount: ₹{amount:,}")
                print(f"   Expected: {test_case['expected'].upper()}")
                
                if decision == test_case['expected'].upper():
                    print(f"   ✅ Decision matches expectation")
                else:
                    print(f"   ⚠️  Decision doesn't match expectation")
                
                print(f"\n📝 FULL JUSTIFICATION:")
                print(f"   {'-' * 60}")
                print(f"   {justification}")
                print(f"   {'-' * 60}")
                
                # Analyze justification quality
                if "DECISION:" in justification and "REASONING:" in justification:
                    print(f"   ✅ Structured response format")
                else:
                    print(f"   ⚠️  Non-structured response format")
                
                if len(justification) > 200:
                    print(f"   ✅ Detailed justification ({len(justification)} characters)")
                else:
                    print(f"   ⚠️  Brief justification ({len(justification)} characters)")
                
                if test_case['expected'] == 'rejected' and ('exclusion' in justification.lower() or 'waiting' in justification.lower() or 'not covered' in justification.lower()):
                    print(f"   ✅ Rejection reason clearly explained")
                elif test_case['expected'] == 'approved' and ('covered' in justification.lower() or 'approved' in justification.lower()):
                    print(f"   ✅ Approval reason clearly explained")
                else:
                    print(f"   ⚠️  Reason could be more specific")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    print("=" * 80)
    print("✅ Justification testing complete!")

if __name__ == "__main__":
    test_justifications() 