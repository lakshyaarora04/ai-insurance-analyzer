#!/usr/bin/env python3
"""
Script to regenerate document chunks with improved chunking strategy
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
import json

def regenerate_chunks():
    print("🔄 Regenerating document chunks with improved strategy...")
    print("=" * 60)
    
    # Document path
    doc_path = "documents/BAJHLIP23020V012223.pdf"
    data_path = "data/BAJHLIP23020V012223.json"
    
    if not os.path.exists(doc_path):
        print(f"❌ Document not found: {doc_path}")
        return
    
    # Read document
    print("📄 Reading document...")
    text = read_document(doc_path)
    print(f"✅ Document read: {len(text)} characters")
    
    # Generate chunks with improved strategy
    print("✂️ Generating chunks with improved strategy...")
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=200)
    print(f"✅ Generated {len(chunks)} chunks")
    
    # Show chunk statistics
    total_chars = sum(len(chunk) for chunk in chunks)
    avg_chunk_size = total_chars / len(chunks) if chunks else 0
    print(f"📊 Total characters: {total_chars}")
    print(f"📊 Average chunk size: {avg_chunk_size:.0f} characters")
    
    # Check for cataract content in chunks
    cataract_chunks = [i for i, chunk in enumerate(chunks) if "cataract" in chunk.lower()]
    print(f"🔍 Chunks containing 'cataract': {len(cataract_chunks)}")
    if cataract_chunks:
        print(f"🔍 Cataract chunk indices: {cataract_chunks}")
    
    # Save chunks
    print("💾 Saving chunks...")
    os.makedirs("data", exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"✅ Chunks saved to: {data_path}")
    
    # Show sample chunks
    print("\n📋 Sample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk[:300] + "..." if len(chunk) > 300 else chunk)
    
    print("\n" + "=" * 60)
    print("✅ Chunk regeneration complete!")

if __name__ == "__main__":
    regenerate_chunks() 