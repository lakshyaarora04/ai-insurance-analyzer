#!/usr/bin/env python3
"""
Test the reasoning tree system for human-readable breakdowns
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks, embed_claim_query
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.evaluator import evaluate_claim
from backend.decision_engine.reasoning_tree import ReasoningEngine
import json

def test_reasoning_tree():
    """Test the reasoning tree system"""
    print("🧪 TESTING REASONING TREE SYSTEM")
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
    
    # Test cases
    test_cases = [
        {
            'name': 'Cataract Surgery - 24 months (Should be APPROVED)',
            'query': {
                'age': 45,
                'gender': 'male',
                'procedure': 'cataract surgery',
                'location': 'Pune',
                'policy_duration_months': 24
            }
        },
        {
            'name': 'Cataract Surgery - 12 months (Should be REJECTED)',
            'query': {
                'age': 45,
                'gender': 'male',
                'procedure': 'cataract surgery',
                'location': 'Pune',
                'policy_duration_months': 12
            }
        },
        {
            'name': 'Dental Treatment - 6 months (Should be REJECTED)',
            'query': {
                'age': 32,
                'gender': 'female',
                'procedure': 'dental treatment',
                'location': 'Mumbai',
                'policy_duration_months': 6
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        # Get query embedding and retrieve relevant chunks
        query_vector = embed_claim_query(test_case['query'])
        results = store.search(query_vector, top_k=5, distance_threshold=3.0)
        
        print(f"Retrieved {len(results)} relevant chunks")
        
        # Evaluate claim with reasoning tree
        decision = evaluate_claim(test_case['query'], results)
        
        print(f"🎯 Decision: {decision['decision'].upper()}")
        print(f"💰 Amount: ₹{decision['amount']:,}")
        print(f"📊 Confidence: {decision['confidence_score']:.1%}")
        
        # Show reasoning breakdown
        print(f"\n🔍 REASONING BREAKDOWN:")
        print(decision['reasoning_breakdown'])
        
        # Show JSON reasoning tree
        print(f"\n📋 JSON REASONING TREE:")
        print(json.dumps(decision['reasoning_tree'], indent=2))
        
        print("\n" + "=" * 60)
    
    print("✅ REASONING TREE TESTING COMPLETE")

def test_reasoning_engine_directly():
    """Test the reasoning engine directly"""
    print("\n🧪 TESTING REASONING ENGINE DIRECTLY")
    print("=" * 60)
    
    reasoning_engine = ReasoningEngine()
    
    # Test with sample data
    query_data = {
        'age': 45,
        'gender': 'male',
        'procedure': 'cataract surgery',
        'location': 'Pune',
        'policy_duration_months': 24
    }
    
    policy_clauses = [
        "Cataract surgery is covered after 24 months waiting period",
        "Dental treatment is excluded unless emergency due to accident",
        "Cosmetic surgery is excluded unless reconstruction after accident"
    ]
    
    # Analyze claim
    reasoning_tree = reasoning_engine.analyze_claim(query_data, policy_clauses)
    
    print("📋 DIRECT REASONING ANALYSIS:")
    print(reasoning_tree.get_human_readable_breakdown())
    
    print(f"\n📊 JSON OUTPUT:")
    print(json.dumps(reasoning_tree.get_json_breakdown(), indent=2))
    
    print("✅ DIRECT REASONING ENGINE TESTING COMPLETE")

if __name__ == "__main__":
    test_reasoning_tree()
    test_reasoning_engine_directly()
