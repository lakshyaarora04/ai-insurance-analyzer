from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks, embed_query
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.evaluator import evaluate_claim
from backend.api.models import Query
import os
import json
import uuid
import traceback
import re
from typing import Optional

router = APIRouter()

# In-memory storage for uploaded files' vector stores and chunks
uploaded_files = {}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".html"]:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT, and HTML files are supported.")

    temp_path = f"temp_{uuid.uuid4().hex}{ext}"
    try:
        # Save uploaded file to a temporary location
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            with open(temp_path, "wb") as f:
                f.write(content)
        except Exception as e:
            print(f"❌ Error saving uploaded file: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

        # Read and process the document
        try:
            text = read_document(temp_path)
            if not text.strip():
                raise HTTPException(status_code=400, detail="No extractable text found in the document.")
        except Exception as e:
            print(f"❌ Error reading document: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"Failed to read document: {str(e)}")

        # Chunking
        try:
            chunks = chunk_text(text)
            if not chunks:
                raise HTTPException(status_code=400, detail="Document could not be chunked (empty or invalid content).")
        except Exception as e:
            print(f"❌ Error chunking document: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to chunk document.")

        # Embedding
        try:
            embeddings = embed_chunks(chunks, fit_vectorizer=True)
            if embeddings is None or len(embeddings) == 0:
                raise HTTPException(status_code=400, detail="Failed to generate embeddings for document.")
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to generate embeddings for document.")

        # Vector store
        try:
            store = VectorStore(dimension=embeddings.shape[1])
            store.add(embeddings, chunks)
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to initialize vector store.")

        # Generate a unique file/session id
        file_id = uuid.uuid4().hex
        uploaded_files[file_id] = {
            "vector_store": store,
            "chunks": chunks,
            "embeddings": embeddings
        }
        return {"file_id": file_id, "num_chunks": len(chunks)}
    except HTTPException as he:
        # Already handled, just re-raise
        raise he
    except Exception as e:
        print(f"❌ Unhandled error in upload endpoint: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error during file upload.")
    finally:
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"❌ Error cleaning up temp file: {e}")
            print(traceback.format_exc())


@router.post("/query/")
async def handle_query(query: Query):
    print(f"\n🔎 Received Query: {query}")

    # Retrieve the correct vector store and chunks using file_id
    file_id = query.file_id
    if not file_id or file_id not in uploaded_files:
        raise HTTPException(status_code=400, detail="Invalid or missing file_id. Please upload a document first and use the returned file_id.")

    store = uploaded_files[file_id]["vector_store"]
    chunks = uploaded_files[file_id]["chunks"]

    # Embed the procedure only for search using the fitted vectorizer
    query_vector = embed_query(query.procedure)
    print(f"🔍 Query vector shape: {query_vector.shape}")

    # Search top 8 matching chunks for better coverage
    results = store.search(query_vector, top_k=8)
    print(f"🔍 Retrieved {len(results)} chunks")

    # Debug print the top matches
    print("\n🔍 Retrieved Chunks:")
    for i, r in enumerate(results):
        print(f"\n--- Chunk {i + 1} ---\n{r}\n")

    # Evaluate decision based on retrieved chunks
    result = evaluate_claim(query.dict(), results)

    print("\n✅ Final Decision:")
    print(result)

    return result


@router.post("/nl_query/")
async def handle_nl_query(
    file_id: str = Body(...),
    query_text: str = Body(..., embed=True)
):
    # Simple rule-based parser for demonstration
    # Extract age, gender, procedure, location, policy_duration_months
    age = None
    gender = None
    procedure = None
    location = None
    policy_duration_months = None

    # Age
    age_match = re.search(r"(\d+)[ -]?year[- ]old", query_text, re.IGNORECASE)
    if age_match:
        age = int(age_match.group(1))

    # Gender
    if re.search(r"\bmale\b", query_text, re.IGNORECASE):
        gender = "male"
    elif re.search(r"\bfemale\b", query_text, re.IGNORECASE):
        gender = "female"

    # Policy duration
    duration_match = re.search(r"(\d+)[ -]?month[s]?", query_text, re.IGNORECASE)
    if duration_match:
        policy_duration_months = int(duration_match.group(1))

    # Location (very basic: look for 'in <location>' or 'to <location>')
    loc_match = re.search(r"(?:in|to) ([A-Z][a-zA-Z]+)", query_text)
    if loc_match:
        location = loc_match.group(1)

    # Procedure/claim type (very basic: look for 'lost', 'surgery', etc.)
    proc_match = re.search(r"lost [a-zA-Z]+|surgery|hospitalization|accident|theft|delay|cancellation", query_text, re.IGNORECASE)
    if proc_match:
        procedure = proc_match.group(0)

    # Build structured query
    structured_query = {
        "file_id": file_id,
        "age": age,
        "gender": gender,
        "procedure": procedure,
        "location": location,
        "policy_duration_months": policy_duration_months
    }

    # Remove None values
    structured_query = {k: v for k, v in structured_query.items() if v is not None}

    # Forward to /query/ endpoint
    return await handle_query(Query(**structured_query))
