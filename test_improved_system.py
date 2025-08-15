#!/usr/bin/env python3
"""
Comprehensive test for the improved LLM-based insurance claim evaluation system
Tests natural language parsing, improved retrieval, and LLM decision making
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks, embed_claim_query
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.evaluator import evaluate_claim
from backend.parser.query_parser import NaturalLanguageQueryParser
import json

def test_natural_language_parsing():
    """Test the improved natural language query parser"""
    print("🧪 TESTING NATURAL LANGUAGE QUERY PARSER")
    print("=" * 60)
    
    parser = NaturalLanguageQueryParser()
    
    test_queries = [
        "I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.",
        "Female patient, 32 years old, wants dental treatment in Mumbai. Policy duration 6 months.",
        "Emergency heart surgery needed for 55-year-old man in Delhi. Policy active for 18 months.",
        "Knee replacement surgery for 65-year-old male in Chennai. 30-month policy.",
        "Cosmetic surgery request from 28-year-old female in Bangalore. 12-month policy.",
        "I need appendectomy surgery. I'm 35, female, in Hyderabad. Policy is 8 months old."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        result = parser.parse_query(query)
        print(f"✅ Parsed Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ NATURAL LANGUAGE PARSER TESTING COMPLETE\n")

def test_vector_retrieval():
    """Test the improved vector retrieval system"""
    print("🧪 TESTING IMPROVED VECTOR RETRIEVAL")
    print("=" * 60)
    
    # Load document and create embeddings
    print("📄 Loading document and creating embeddings...")
    doc_path = "documents/BAJHLIP23020V012223.pdf"
    text = read_document(doc_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks, fit_vectorizer=True)
    
    # Create vector store
    store = VectorStore(dimension=len(embeddings[0]))
    store.add(embeddings, chunks)
    
    # Test different query types
    test_queries = [
        {
            'procedure': 'cataract surgery',
            'location': 'Pune',
            'policy_duration_months': 24
        },
        {
            'procedure': 'dental treatment',
            'location': 'Mumbai',
            'policy_duration_months': 6
        },
        {
            'procedure': 'heart surgery',
            'location': 'Delhi',
            'policy_duration_months': 18
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query['procedure']} in {query['location']}")
        query_vector = embed_claim_query(query)
        results = store.search(query_vector, top_k=5, distance_threshold=3.0)
        
        print(f"✅ Retrieved {len(results)} relevant chunks")
        for j, chunk in enumerate(results[:3]):  # Show first 3 chunks
            print(f"   Chunk {j+1}: {chunk[:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ VECTOR RETRIEVAL TESTING COMPLETE\n")

def test_llm_decision_making():
    """Test the LLM decision making with actual policy context"""
    print("🧪 TESTING LLM DECISION MAKING")
    print("=" * 60)
    
    # Load document and create embeddings
    print("📄 Loading document and creating embeddings...")
    doc_path = "documents/BAJHLIP23020V012223.pdf"
    text = read_document(doc_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks, fit_vectorizer=True)
    
    # Create vector store
    store = VectorStore(dimension=len(embeddings[0]))
    store.add(embeddings, chunks)
    
    # Test cases with expected outcomes
    test_cases = [
        {
            'name': 'Cataract Surgery - 24 months (Should be APPROVED)',
            'query': {
                'age': 45,
                'gender': 'male',
                'procedure': 'cataract surgery',
                'location': 'Pune',
                'policy_duration_months': 24
            },
            'expected': 'approved'
        },
        {
            'name': 'Cataract Surgery - 12 months (Should be REJECTED)',
            'query': {
                'age': 45,
                'gender': 'male',
                'procedure': 'cataract surgery',
                'location': 'Pune',
                'policy_duration_months': 12
            },
            'expected': 'rejected'
        },
        {
            'name': 'Dental Treatment - 6 months (Should be REJECTED)',
            'query': {
                'age': 32,
                'gender': 'female',
                'procedure': 'dental treatment',
                'location': 'Mumbai',
                'policy_duration_months': 6
            },
            'expected': 'rejected'
        },
        {
            'name': 'Heart Surgery - 18 months (Should be APPROVED)',
            'query': {
                'age': 55,
                'gender': 'male',
                'procedure': 'heart surgery',
                'location': 'Delhi',
                'policy_duration_months': 18
            },
            'expected': 'approved'
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 50)
        
        # Get query embedding and retrieve relevant chunks
        query_vector = embed_claim_query(test_case['query'])
        results = store.search(query_vector, top_k=5, distance_threshold=3.0)
        
        print(f"Retrieved {len(results)} relevant chunks")
        
        # Evaluate claim
        decision = evaluate_claim(test_case['query'], results)
        
        print(f"Decision: {decision['decision'].upper()}")
        print(f"Amount: ₹{decision['amount']:,}")
        print(f"Expected: {test_case['expected'].upper()}")
        
        # Check if decision matches expectation
        if decision['decision'] == test_case['expected']:
            print("✅ Decision matches expectation")
            successful_tests += 1
        else:
            print("❌ Decision does not match expectation")
        
        # Show justification
        print(f"Justification: {decision['justification'][:200]}...")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the results above.")
    
    print("\n" + "=" * 60)
    print("✅ LLM DECISION MAKING TESTING COMPLETE\n")

def test_end_to_end():
    """Test the complete end-to-end system with natural language input"""
    print("🧪 TESTING END-TO-END SYSTEM")
    print("=" * 60)
    
    # Load document and create embeddings
    print("📄 Loading document and creating embeddings...")
    doc_path = "documents/BAJHLIP23020V012223.pdf"
    text = read_document(doc_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks, fit_vectorizer=True)
    
    # Create vector store
    store = VectorStore(dimension=len(embeddings[0]))
    store.add(embeddings, chunks)
    
    # Initialize parser
    parser = NaturalLanguageQueryParser()
    
    # Test natural language queries
    natural_queries = [
        "I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.",
        "Female patient, 32 years old, wants dental treatment in Mumbai. Policy duration 6 months.",
        "Emergency heart surgery needed for 55-year-old man in Delhi. Policy active for 18 months."
    ]
    
    for i, query in enumerate(natural_queries, 1):
        print(f"\n📝 Natural Language Query {i}: {query}")
        print("-" * 50)
        
        # Parse natural language query
        structured_query = parser.parse_query(query)
        print(f"✅ Parsed to: {json.dumps(structured_query, indent=2)}")
        
        # Get query embedding and retrieve relevant chunks
        query_vector = embed_claim_query(structured_query)
        results = store.search(query_vector, top_k=5, distance_threshold=3.0)
        
        print(f"Retrieved {len(results)} relevant chunks")
        
        # Evaluate claim
        decision = evaluate_claim(structured_query, results)
        
        print(f"Final Decision: {decision['decision'].upper()}")
        print(f"Amount: ₹{decision['amount']:,}")
        print(f"Justification: {decision['justification'][:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ END-TO-END TESTING COMPLETE")

def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE SYSTEM TESTING")
    print("=" * 80)
    
    try:
        # Test 1: Natural language parsing
        test_natural_language_parsing()
        
        # Test 2: Vector retrieval
        test_vector_retrieval()
        
        # Test 3: LLM decision making
        test_llm_decision_making()
        
        # Test 4: End-to-end system
        test_end_to_end()
        
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
