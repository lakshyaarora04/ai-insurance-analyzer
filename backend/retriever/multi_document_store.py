"""
Multi-Document Reasoning System
Supports searching across multiple policy documents (base policy + rider + email)
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from backend.retriever.vector_store import VectorStore
from backend.retriever.embedder import embed_chunks, embed_claim_query
from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text

@dataclass
class DocumentInfo:
    """Information about a document in the multi-document store"""
    name: str
    type: str  # 'base_policy', 'rider', 'email', 'amendment'
    file_path: str
    chunk_count: int
    document_id: str

class MultiDocumentStore:
    """
    Manages multiple policy documents and provides unified search
    """
    
    def __init__(self):
        self.documents: Dict[str, DocumentInfo] = {}
        self.vector_stores: Dict[str, VectorStore] = {}
        self.global_vector_store: Optional[VectorStore] = None
        self.global_chunks: List[str] = []
        self.global_embeddings: List[List[float]] = []
        self.document_mapping: List[Tuple[str, int]] = []  # (doc_id, chunk_index)
    
    def add_document(self, file_path: str, doc_type: str = "base_policy", 
                    document_name: str = None) -> str:
        """
        Add a document to the multi-document store
        
        Args:
            file_path: Path to the document file
            doc_type: Type of document ('base_policy', 'rider', 'email', 'amendment')
            document_name: Optional name for the document
            
        Returns:
            Document ID
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Generate document ID
        doc_id = f"{doc_type}_{len(self.documents)}"
        
        # Read and chunk document
        print(f"📄 Loading document: {file_path}")
        text = read_document(file_path)
        chunks = chunk_text(text)
        
        # Store document info first
        doc_name = document_name or os.path.basename(file_path)
        doc_info = DocumentInfo(
            name=doc_name,
            type=doc_type,
            file_path=file_path,
            chunk_count=len(chunks),
            document_id=doc_id
        )
        
        self.documents[doc_id] = doc_info
        
        # Add chunks to global store first (before creating embeddings)
        start_index = len(self.global_chunks)
        self.global_chunks.extend(chunks)
        
        # Update document mapping
        for i in range(len(chunks)):
            self.document_mapping.append((doc_id, i))
        
        # Store chunks for later embedding (we'll fit vectorizer on all chunks at once)
        if not hasattr(self, 'pending_chunks'):
            self.pending_chunks = []
        self.pending_chunks.extend(chunks)
        
        print(f"✅ Added document '{doc_name}' ({doc_type}) with {len(chunks)} chunks")
        return doc_id
    
    def finalize_documents(self):
        """
        Finalize document processing by fitting vectorizer on all chunks
        This must be called after adding all documents
        """
        if not hasattr(self, 'pending_chunks') or not self.pending_chunks:
            print("⚠️  No documents to finalize")
            return
        
        print(f"🔧 Fitting vectorizer on {len(self.pending_chunks)} total chunks")
        
        # Fit vectorizer on all chunks at once
        all_embeddings = embed_chunks(self.pending_chunks, fit_vectorizer=True)
        
        # Create individual vector stores for each document
        chunk_start = 0
        for doc_id, doc_info in self.documents.items():
            # Get chunks for this document
            doc_chunks = self.global_chunks[chunk_start:chunk_start + doc_info.chunk_count]
            doc_embeddings = all_embeddings[chunk_start:chunk_start + doc_info.chunk_count]
            
            # Create individual vector store
            individual_store = VectorStore(dimension=len(doc_embeddings[0]))
            individual_store.add(doc_embeddings, doc_chunks)
            self.vector_stores[doc_id] = individual_store
            
            # Add to global embeddings
            self.global_embeddings.extend(doc_embeddings)
            
            chunk_start += doc_info.chunk_count
        
        # Create global vector store
        if self.global_embeddings:
            self.global_vector_store = VectorStore(dimension=len(self.global_embeddings[0]))
            self.global_vector_store.add(self.global_embeddings, self.global_chunks)
        
        # Clear pending chunks
        self.pending_chunks = []
        
        print(f"✅ Finalized {len(self.documents)} documents with {len(self.global_chunks)} total chunks")
    

    
    def search_across_all_documents(self, query_data: Dict[str, Any], 
                                   top_k: int = 10, 
                                   distance_threshold: float = 3.0) -> List[Dict[str, Any]]:
        """
        Search across all documents and return results with document context
        
        Returns:
            List of results with document information
        """
        if not self.global_vector_store:
            return []
        
        # Get query embedding
        query_vector = embed_claim_query(query_data)
        
        # Search in global store
        results = self.global_vector_store.search(query_vector, top_k, distance_threshold)
        
        # Add document context to results
        enriched_results = []
        for i, chunk in enumerate(results):
            # Find which document this chunk belongs to
            chunk_index = self.global_chunks.index(chunk)
            doc_id, local_index = self.document_mapping[chunk_index]
            doc_info = self.documents[doc_id]
            
            enriched_results.append({
                'chunk': chunk,
                'document_id': doc_id,
                'document_name': doc_info.name,
                'document_type': doc_info.type,
                'chunk_index': local_index,
                'global_index': chunk_index
            })
        
        return enriched_results
    
    def search_by_document_type(self, query_data: Dict[str, Any], 
                               doc_type: str, 
                               top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search only in documents of a specific type
        
        Args:
            query_data: Query data
            doc_type: Document type to search in
            top_k: Number of results to return
            
        Returns:
            List of results from specified document type
        """
        # Find documents of the specified type
        target_docs = [doc_id for doc_id, doc_info in self.documents.items() 
                      if doc_info.type == doc_type]
        
        if not target_docs:
            return []
        
        # Search in each document and combine results
        all_results = []
        query_vector = embed_claim_query(query_data)
        
        for doc_id in target_docs:
            store = self.vector_stores[doc_id]
            results = store.search(query_vector, top_k, 3.0)
            
            doc_info = self.documents[doc_id]
            for chunk in results:
                all_results.append({
                    'chunk': chunk,
                    'document_id': doc_id,
                    'document_name': doc_info.name,
                    'document_type': doc_info.type
                })
        
        # Sort by relevance and return top_k
        return all_results[:top_k]
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of all documents in the store"""
        summary = {
            'total_documents': len(self.documents),
            'total_chunks': len(self.global_chunks),
            'documents': {}
        }
        
        for doc_id, doc_info in self.documents.items():
            summary['documents'][doc_id] = {
                'name': doc_info.name,
                'type': doc_info.type,
                'chunk_count': doc_info.chunk_count,
                'file_path': doc_info.file_path
            }
        
        return summary
    
    def get_chunks_by_document(self, doc_id: str) -> List[str]:
        """Get all chunks from a specific document"""
        if doc_id not in self.documents:
            return []
        
        # Find chunks belonging to this document
        chunks = []
        for i, (doc_id_mapping, _) in enumerate(self.document_mapping):
            if doc_id_mapping == doc_id:
                chunks.append(self.global_chunks[i])
        
        return chunks
    
    def get_chunks_by_type(self, doc_type: str) -> List[str]:
        """Get all chunks from documents of a specific type"""
        chunks = []
        for doc_id, doc_info in self.documents.items():
            if doc_info.type == doc_type:
                doc_chunks = self.get_chunks_by_document(doc_id)
                chunks.extend(doc_chunks)
        
        return chunks

class MultiDocumentReasoningEngine:
    """
    Advanced reasoning engine that considers multiple documents
    """
    
    def __init__(self, multi_doc_store: MultiDocumentStore):
        self.store = multi_doc_store
    
    def analyze_claim_with_multiple_documents(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze claim considering all available documents
        
        Returns:
            Comprehensive analysis with document-specific insights
        """
        # Search across all documents
        all_results = self.store.search_across_all_documents(query_data, top_k=15)
        
        # Group results by document type
        results_by_type = {}
        for result in all_results:
            doc_type = result['document_type']
            if doc_type not in results_by_type:
                results_by_type[doc_type] = []
            results_by_type[doc_type].append(result)
        
        # Analyze each document type
        analysis = {
            'query_data': query_data,
            'total_chunks_found': len(all_results),
            'document_analysis': {},
            'conflicting_clauses': [],
            'supporting_clauses': [],
            'exclusion_clauses': []
        }
        
        for doc_type, results in results_by_type.items():
            analysis['document_analysis'][doc_type] = {
                'chunks_found': len(results),
                'documents': list(set(r['document_name'] for r in results)),
                'relevant_clauses': [r['chunk'] for r in results]
            }
        
        # Identify conflicts and supports
        self._identify_conflicts_and_supports(analysis, all_results)
        
        return analysis
    
    def _identify_conflicts_and_supports(self, analysis: Dict[str, Any], results: List[Dict[str, Any]]):
        """Identify conflicting and supporting clauses across documents"""
        procedure = analysis['query_data'].get('procedure', '').lower()
        
        for result in results:
            chunk = result['chunk'].lower()
            doc_type = result['document_type']
            
            # Check for supporting clauses
            if procedure in chunk and any(word in chunk for word in ['covered', 'included', 'eligible']):
                analysis['supporting_clauses'].append({
                    'clause': result['chunk'],
                    'document': result['document_name'],
                    'type': doc_type
                })
            
            # Check for exclusion clauses
            if any(word in chunk for word in ['excluded', 'not covered', 'not eligible']):
                analysis['exclusion_clauses'].append({
                    'clause': result['chunk'],
                    'document': result['document_name'],
                    'type': doc_type
                })
        
        # Check for conflicts between base policy and riders
        base_clauses = analysis['document_analysis'].get('base_policy', {}).get('relevant_clauses', [])
        rider_clauses = analysis['document_analysis'].get('rider', {}).get('relevant_clauses', [])
        
        if base_clauses and rider_clauses:
            # Simple conflict detection (can be enhanced)
            for base_clause in base_clauses:
                for rider_clause in rider_clauses:
                    if self._clauses_conflict(base_clause, rider_clause):
                        analysis['conflicting_clauses'].append({
                            'base_policy_clause': base_clause,
                            'rider_clause': rider_clause
                        })
    
    def _clauses_conflict(self, clause1: str, clause2: str) -> bool:
        """Check if two clauses conflict with each other"""
        # Simple conflict detection - can be enhanced with LLM
        clause1_lower = clause1.lower()
        clause2_lower = clause2.lower()
        
        # Check for opposite keywords
        if ('covered' in clause1_lower and 'excluded' in clause2_lower) or \
           ('excluded' in clause1_lower and 'covered' in clause2_lower):
            return True
        
        return False
