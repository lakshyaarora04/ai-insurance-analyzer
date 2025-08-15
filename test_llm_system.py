import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks, embed_claim_query
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.evaluator import evaluate_claim
import json

def test_system():
    print("🧪 TESTING LLM-BASED INSURANCE CLAIM SYSTEM")
    print("=" * 60)
    
    # Test case 1: Cataract surgery with 24 months policy duration (should be approved)
    test_query_1 = {
        'age': 40,
        'gender': 'male', 
        'procedure': 'cataract surgery',
        'location': 'Pune',
        'policy_duration_months': 24
    }
    
    # Test case 2: Cataract surgery with 12 months policy duration (should be rejected due to waiting period)
    test_query_2 = {
        'age': 40,
        'gender': 'male', 
        'procedure': 'cataract surgery',
        'location': 'Pune',
        'policy_duration_months': 12
    }
    
    # Load document and create embeddings
    print("📄 Loading document and creating embeddings...")
    doc_path = "documents/BAJHLIP23020V012223.pdf"
    text = read_document(doc_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks, fit_vectorizer=True)  # Fit vectorizer on document chunks
    
    # Create vector store
    store = VectorStore(dimension=len(embeddings[0]))
    store.add(embeddings, chunks)
    print(f"✅ Loaded {len(chunks)} chunks into vector store")
    
    # Test case 1
    print(f"\n🔍 TEST CASE 1: {test_query_1['procedure']} with {test_query_1['policy_duration_months']} months policy")
    print("-" * 50)
    
    # Use improved query embedding
    query_vector_1 = embed_claim_query(test_query_1)
    results_1 = store.search(query_vector_1, top_k=5, distance_threshold=3.0)
    
    print(f"Retrieved {len(results_1)} relevant chunks")
    for i, chunk in enumerate(results_1):
        print(f"Chunk {i+1}: {chunk[:200]}...")
    
    decision_1 = evaluate_claim(test_query_1, results_1)
    print(f"\nDecision: {decision_1['decision'].upper()}")
    print(f"Amount: ₹{decision_1['amount']}")
    print(f"Justification: {decision_1['justification']}")
    
    # Test case 2
    print(f"\n🔍 TEST CASE 2: {test_query_2['procedure']} with {test_query_2['policy_duration_months']} months policy")
    print("-" * 50)
    
    # Use improved query embedding
    query_vector_2 = embed_claim_query(test_query_2)
    results_2 = store.search(query_vector_2, top_k=5, distance_threshold=3.0)
    
    print(f"Retrieved {len(results_2)} relevant chunks")
    for i, chunk in enumerate(results_2):
        print(f"Chunk {i+1}: {chunk[:200]}...")
    
    decision_2 = evaluate_claim(test_query_2, results_2)
    print(f"\nDecision: {decision_2['decision'].upper()}")
    print(f"Amount: ₹{decision_2['amount']}")
    print(f"Justification: {decision_2['justification']}")
    
    print("\n" + "=" * 60)
    print("✅ TESTING COMPLETE")

if __name__ == "__main__":
    test_system() 