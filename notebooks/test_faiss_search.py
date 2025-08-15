import sys
import os

# 🔧 Add root directory to sys.path so we can import backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.retriever.embedder import embed_chunks
from backend.retriever.vector_store import VectorStore





import json
import os
from backend.retriever.embedder import embed_chunks
from backend.retriever.vector_store import VectorStore

# Step 1: Load chunks
with open("data/sample_policy.pdf.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Step 2: Embed them
embeddings = embed_chunks(chunks)

# Step 3: Store them in FAISS
store = VectorStore(dimension=len(embeddings[0]))
store.add(embeddings, chunks)

# Step 4: Embed a question
question = "Is knee surgery covered?"
query_embedding = embed_chunks([question])[0]

# Step 5: Search
results = store.search(query_embedding, top_k=2)

# Step 6: Print results
print("\n🔍 Top matching chunks:\n")
for i, chunk in enumerate(results, 1):
    print(f"{i}. {chunk}\n")


from backend.decision_engine.evaluator import evaluate_claim

# Simulate parsed query
query_info = {
    "age": 46,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Pune",
    "policy_duration_months": 3
}

decision = evaluate_claim(query_info, results)

print("\n✅ Final Decision:\n")
print(decision)
