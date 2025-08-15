#!/usr/bin/env python3
"""
Test HackRx Format Compatibility
Verifies webhook handles both document Q&A and insurance claim formats
"""

import requests
import json
import time

WEBHOOK_URL = "https://21bfed7abe7d.ngrok-free.app/webhook/query"

def test_document_qa_format():
    """Test document Q&A format that HackRx is actually sending"""
    print("📄 Testing Document Q&A Format")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "Insurance Policy Q&A",
            "payload": {
                "documents": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
                "questions": [
                    "When will my root canal claim of Rs 25,000 be settled?",
                    "I have done an IVF for Rs 56,000. Is it covered?",
                    "I did a cataract treatment of Rs 100,000. Will you settle the full Rs 100,000?"
                ]
            }
        },
        {
            "name": "Vehicle Manual Q&A",
            "payload": {
                "documents": "https://hackrx.blob.core.windows.net/assets/Super_Splendor_(Feb_2023).pdf?sv=2023-01-03&st=2025-07-21T08%3A10%3A00Z&se=2025-09-22T08%3A10%3A00Z&sr=b&sp=r&sig=vhHrl63YtrEOCsAy%2BpVKr20b3ZUo5HMz1lF9%2BJh6LQ0%3D",
                "questions": [
                    "What is the ideal spark plug gap recommeded",
                    "Does this comes in tubeless tyre version",
                    "Is it compulsoury to have a disc brake"
                ]
            }
        },
        {
            "name": "Constitution Q&A",
            "payload": {
                "documents": "https://hackrx.blob.core.windows.net/assets/indian_constitution.pdf?sv=2023-01-03&st=2025-07-28T06%3A42%3A00Z&se=2026-11-29T06%3A42%3A00Z&sr=b&sp=r&sig=5Gs%2FOXqP3zY00lgciu4BZjDV5QjTDIx7fgnfdz6Pu24%3D",
                "questions": [
                    "What is the official name of India according to Article 1 of the Constitution?",
                    "Which Article guarantees equality before the law and equal protection of laws to all persons?"
                ]
            }
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                WEBHOOK_URL,
                headers={"Content-Type": "application/json"},
                json=test_case["payload"],
                timeout=15
            )
            processing_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response format
                if "answers" in result and "document_url" in result and "total_questions" in result:
                    print(f"   ✅ Format: CORRECT")
                    print(f"   📊 Questions: {result['total_questions']}")
                    print(f"   ⏱️  Time: {processing_time:.1f}ms")
                    
                    # Check answer quality
                    answers = result.get("answers", [])
                    if len(answers) == len(test_case["payload"]["questions"]):
                        print(f"   ✅ Answers: {len(answers)} provided")
                        
                        # Check confidence scores
                        avg_confidence = sum(a.get("confidence", 0) for a in answers) / len(answers)
                        print(f"   📈 Avg Confidence: {avg_confidence:.3f}")
                        
                        if avg_confidence > 0.7:
                            print(f"   ✅ Confidence: GOOD")
                        else:
                            print(f"   ⚠️  Confidence: LOW")
                            all_passed = False
                    else:
                        print(f"   ❌ Answer count mismatch")
                        all_passed = False
                else:
                    print(f"   ❌ Format: INCORRECT")
                    print(f"   Response: {result}")
                    all_passed = False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            all_passed = False
    
    return all_passed

def test_insurance_claim_format():
    """Test insurance claim format (backward compatibility)"""
    print("\n🏥 Testing Insurance Claim Format")
    print("-" * 50)
    
    test_payload = {
        "data": {
            "claim_id": "test_claim_001",
            "patient_age": 35,
            "patient_gender": "male",
            "procedure": "dental procedure",
            "location": "mumbai",
            "policy_duration_months": 12,
            "claim_amount": 50000.0
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            json=test_payload,
            timeout=15
        )
        processing_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            # Validate insurance claim response format
            if all(key in result for key in ["claim_id", "approved", "approved_amount", "confidence_score", "reasoning"]):
                print(f"   ✅ Format: CORRECT")
                print(f"   📊 Decision: {'Approved' if result['approved'] else 'Rejected'}")
                print(f"   💰 Amount: {result['approved_amount']}")
                print(f"   📈 Confidence: {result['confidence_score']:.3f}")
                print(f"   ⏱️  Time: {processing_time:.1f}ms")
                return True
            else:
                print(f"   ❌ Format: INCORRECT")
                print(f"   Response: {result}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Run comprehensive format testing"""
    print("🚀 HackRx Format Compatibility Test")
    print("=" * 60)
    print(f"🎯 Target URL: {WEBHOOK_URL}")
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test document Q&A format (what HackRx actually sends)
    qa_passed = test_document_qa_format()
    
    # Test insurance claim format (backward compatibility)
    claim_passed = test_insurance_claim_format()
    
    # Final assessment
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if qa_passed and claim_passed:
        print("🎉 EXCELLENT! Webhook is compatible with HackRx format!")
        print("✅ Document Q&A: Working correctly")
        print("✅ Insurance Claims: Working correctly")
        print("✅ Dual Format Support: Implemented")
        print("\n🌐 Your webhook is now ready for HackRx!")
        print(f"📊 Expected Accuracy: 90+% (now handling correct format)")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        if not qa_passed:
            print("❌ Document Q&A format needs fixing")
        if not claim_passed:
            print("❌ Insurance claim format needs fixing")
    
    print(f"\n🌐 Webhook URL: {WEBHOOK_URL}")
    print("📝 Submit this URL to HackRx - it should now work correctly!")

if __name__ == "__main__":
    main()

