#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""

import requests
import json

def test_system():
    print("🧪 Testing the system...")
    
    # Test query
    test_data = {
        "age": 40,
        "gender": "male",
        "procedure": "cataract surgery",
        "location": "Pune",
        "policy_duration_months": 24
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/query/",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ System is working!")
            print(f"Decision: {result.get('decision', 'N/A')}")
            print(f"Amount: ₹{result.get('amount', 0)}")
            print(f"Retrieved chunks: {result.get('retrieved_chunks', 'N/A')}")
            print(f"Justification: {result.get('justification', 'N/A')[:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_system() 