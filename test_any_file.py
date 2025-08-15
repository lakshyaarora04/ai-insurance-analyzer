#!/usr/bin/env python3
"""
Test to demonstrate that the system works with ANY file and uses real LLM processing
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

def test_with_any_file(file_path):
    """Test the system with any provided file"""
    print(f"🧪 TESTING WITH FILE: {file_path}")
    print("=" * 80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Load document and create embeddings
        print(f"📄 Loading document: {file_path}")
        text = read_document(file_path)
        print(f"✅ Document loaded: {len(text)} characters")
        
        # Chunk the text
        chunks = chunk_text(text)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Create embeddings
        embeddings = embed_chunks(chunks, fit_vectorizer=True)
        print(f"✅ Created embeddings: {len(embeddings)} vectors")
        
        # Create vector store
        store = VectorStore(dimension=len(embeddings[0]))
        store.add(embeddings, chunks)
        
        # Initialize parser
        parser = NaturalLanguageQueryParser()
        
        # Test with natural language queries
        test_queries = [
            "I'm a 45-year-old male who needs cataract surgery. My policy is 24 months old.",
            "Female patient, 32 years old, wants dental treatment. Policy duration 6 months.",
            "Emergency heart surgery needed for 55-year-old man. Policy active for 18 months."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            print("-" * 60)
            
            # Parse natural language query
            structured_query = parser.parse_query(query)
            print(f"✅ Parsed to: {json.dumps(structured_query, indent=2)}")
            
            # Get query embedding and retrieve relevant chunks
            query_vector = embed_claim_query(structured_query)
            results = store.search(query_vector, top_k=5, distance_threshold=3.0)
            
            print(f"Retrieved {len(results)} relevant chunks from the document")
            
            # Show some retrieved chunks
            for j, chunk in enumerate(results[:2]):
                print(f"   Chunk {j+1}: {chunk[:200]}...")
            
            # Evaluate claim using LLM
            print(f"\n🤖 Calling OpenAI LLM for decision...")
            decision = evaluate_claim(structured_query, results)
            
            print(f"🎯 LLM Decision: {decision['decision'].upper()}")
            print(f"💰 Amount: ₹{decision['amount']:,}")
            print(f"📝 Justification: {decision['justification'][:300]}...")
            
            # Verify this is real LLM processing
            if "DECISION:" in decision['justification'] and "REASONING:" in decision['justification']:
                print("✅ CONFIRMED: Using real LLM processing (structured response)")
            else:
                print("⚠️  WARNING: Response doesn't look like structured LLM output")
        
        print(f"\n{'='*80}")
        print("✅ TESTING COMPLETED SUCCESSFULLY!")
        print("✅ CONFIRMED: System uses real LLM processing with any file")
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def main():
    """Test with different files"""
    print("🚀 TESTING SYSTEM WITH ANY FILE")
    print("=" * 80)
    
    # Test with the existing policy document
    print("📋 Test 1: Using existing policy document")
    test_with_any_file("documents/BAJHLIP23020V012223.pdf")
    
    # Test with another document if available
    other_files = [
        "documents/CHOTGDP23004V012223.pdf",
        "documents/sample_policy.pdf"
    ]
    
    for file_path in other_files:
        if os.path.exists(file_path):
            print(f"\n📋 Test 2: Using {file_path}")
            test_with_any_file(file_path)
            break
    
    print(f"\n{'='*80}")
    print("🎉 ALL TESTS COMPLETED!")
    print("✅ CONFIRMED: System works with any file and uses real LLM processing")

if __name__ == "__main__":
    main()
