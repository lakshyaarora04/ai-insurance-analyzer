#!/usr/bin/env python3
"""
Debug test to see what's happening with decision parsing
"""

import requests
import json

def test_debug():
    print("🔍 DEBUG TEST - Dental Treatment")
    print("=" * 60)
    
    query = {
        "age": 28,
        "gender": "female",
        "procedure": "dental treatment",
        "location": "Bangalore",
        "policy_duration_months": 3
    }
    
    print(f"Query: {json.dumps(query, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/query/",
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 RESULT:")
            print(f"   Decision: {result.get('decision', 'N/A').upper()}")
            print(f"   Amount: ₹{result.get('amount', 0):,}")
            
            justification = result.get('justification', 'N/A')
            print(f"\n📝 FULL JUSTIFICATION:")
            print(f"   {'-' * 50}")
            print(f"   {justification}")
            print(f"   {'-' * 50}")
            
            # Check if LLM said approved but system shows rejected
            if "DECISION: APPROVED" in justification.upper() and result.get('decision') == 'rejected':
                print(f"\n⚠️  ISSUE: LLM said APPROVED but system shows REJECTED")
            elif "DECISION: REJECTED" in justification.upper() and result.get('decision') == 'approved':
                print(f"\n⚠️  ISSUE: LLM said REJECTED but system shows APPROVED")
            else:
                print(f"\n✅ Decision parsing looks correct")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_debug() 