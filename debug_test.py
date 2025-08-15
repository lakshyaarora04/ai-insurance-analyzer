import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.evaluator import evaluate_claim
import json

# Test query
test_query = {
    'age': 40,
    'gender': 'male', 
    'procedure': 'cataract surgery',
    'location': 'Pune',
    'policy_duration_months': 24
}

print("🔍 DEBUGGING THE SYSTEM STEP BY STEP")
print("=" * 50)

# Step 1: Check if document is being read correctly
print("\n1. CHECKING DOCUMENT READING:")
doc_path = "documents/BAJHLIP23020V012223.pdf"
if os.path.exists(doc_path):
    print(f"✅ Document exists: {doc_path}")
    text = read_document(doc_path)
    print(f"✅ Document text length: {len(text)} characters")
    
    # Check if cataract is in the raw text
    if "cataract" in text.lower():
        print("✅ 'cataract' found in raw document text")
    else:
        print("❌ 'cataract' NOT found in raw document text")
else:
    print(f"❌ Document not found: {doc_path}")
    exit(1)

# Step 2: Check chunking
print("\n2. CHECKING CHUNKING:")
chunks = chunk_text(text)
print(f"✅ Created {len(chunks)} chunks")

# Check if cataract is in any chunks
cataract_chunks = [i for i, chunk in enumerate(chunks) if "cataract" in chunk.lower()]
if cataract_chunks:
    print(f"✅ 'cataract' found in chunks: {cataract_chunks}")
    print(f"Sample chunk with cataract: {chunks[cataract_chunks[0]][:200]}...")
else:
    print("❌ 'cataract' NOT found in any chunks")

# Step 3: Check embeddings
print("\n3. CHECKING EMBEDDINGS:")
embeddings = embed_chunks(chunks)
print(f"✅ Created {len(embeddings)} embeddings")
print(f"✅ Embedding dimension: {len(embeddings[0])}")

# Step 4: Check vector store
print("\n4. CHECKING VECTOR STORE:")
store = VectorStore(dimension=len(embeddings[0]))
store.add(embeddings, chunks)
print(f"✅ Added {len(chunks)} chunks to vector store")

# Step 5: Test search
print("\n5. TESTING SEARCH:")
query_vector = embed_chunks([test_query['procedure']])[0]
results = store.search(query_vector, top_k=3)

print(f"✅ Retrieved {len(results)} results")
for i, result in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(f"Length: {len(result)} characters")
    print(f"Content: {result[:300]}...")
    
    # Check if this result contains cataract
    if "cataract" in result.lower():
        print("✅ This result contains 'cataract'")
    else:
        print("❌ This result does NOT contain 'cataract'")

# Step 6: Test decision engine
print("\n6. TESTING DECISION ENGINE:")
decision = evaluate_claim(test_query, results)
print(f"✅ Decision: {decision}")

# Step 7: Check if the issue is in the decision logic
print("\n7. ANALYZING DECISION LOGIC:")
procedure = test_query['procedure'].lower()
policy_duration = test_query['policy_duration_months']

print(f"Looking for procedure: '{procedure}'")
print(f"Policy duration: {policy_duration} months")

for i, chunk in enumerate(results):
    print(f"\n--- Analyzing chunk {i+1} ---")
    chunk_lower = chunk.lower()
    
    if procedure in chunk_lower:
        print(f"✅ Found procedure '{procedure}' in chunk")
        
        if "2 year" in chunk_lower or "24 months" in chunk_lower:
            print(f"✅ Found 2-year waiting period mention")
            if policy_duration < 24:
                print(f"❌ Policy duration ({policy_duration}) < 24 months - should reject")
            else:
                print(f"✅ Policy duration ({policy_duration}) >= 24 months - should approve")
        else:
            print(f"❌ No 2-year waiting period mention found")
    else:
        print(f"❌ Procedure '{procedure}' NOT found in chunk")

print("\n" + "=" * 50)
print("DEBUG COMPLETE") 