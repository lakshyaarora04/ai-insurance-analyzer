import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.retriever.embedder import embed_chunks



import json
import os
from backend.retriever.embedder import embed_chunks

path = "data/sample_policy.pdf.json"

with open(path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

embeddings = embed_chunks(chunks)

print(f"✅ Generated {len(embeddings)} embeddings.")
print(f"📐 Shape of each: {len(embeddings[0])} dimensions")
