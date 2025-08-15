import sys
import os

# 👇 Adds the parent directory (project root) to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.utils.document_reader import read_document
from backend.utils.text_chunker import chunk_text




import os
import json
from backend.utils.document_reader import read_document
from backend.utils.text_chunker import chunk_text

doc_folder = "documents"
output_folder = "data"

for filename in os.listdir(doc_folder):
    if not filename.endswith((".pdf", ".docx")):
        continue

    path = os.path.join(doc_folder, filename)
    text = read_document(path)
    chunks = chunk_text(text)

    print(f"📄 {filename}: {len(chunks)} chunks")

    out_path = os.path.join(output_folder, f"{filename}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
