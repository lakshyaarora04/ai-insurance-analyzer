import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 = Euclidean distance
        self.text_chunks = []  # Keep text alongside vectors

    def add(self, embeddings, chunks):
        if len(embeddings) == 0:
            return
            
        vectors = np.array(embeddings).astype("float32")
        
        # Ensure vectors have the correct dimension
        if vectors.shape[1] != self.dimension:
            print(f"Warning: Embedding dimension {vectors.shape[1]} doesn't match expected {self.dimension}")
            # Pad or truncate if necessary
            if vectors.shape[1] < self.dimension:
                # Pad with zeros
                padding = np.zeros((vectors.shape[0], self.dimension - vectors.shape[1]))
                vectors = np.hstack([vectors, padding])
            else:
                # Truncate
                vectors = vectors[:, :self.dimension]
        
        self.index.add(vectors)
        self.text_chunks.extend(chunks)
        print(f"✅ Added {len(chunks)} chunks to vector store")

    def search(self, query_embedding, top_k=5, distance_threshold=2.0):
        """
        Search for similar chunks using FAISS.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            distance_threshold: Maximum distance (higher threshold = more results)
        """
        if len(self.text_chunks) == 0:
            print("⚠️  No chunks in vector store")
            return []
            
        query = np.array([query_embedding]).astype("float32")
        
        # Ensure query has correct dimension
        if query.shape[1] != self.dimension:
            if query.shape[1] < self.dimension:
                padding = np.zeros((query.shape[0], self.dimension - query.shape[1]))
                query = np.hstack([query, padding])
            else:
                query = query[:, :self.dimension]
        
        # Search for similar vectors
        distances, indices = self.index.search(query, min(top_k * 2, len(self.text_chunks)))
        
        # Filter results based on distance threshold and return top_k
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.text_chunks) and dist < distance_threshold:
                results.append(self.text_chunks[idx])
                if len(results) >= top_k:
                    break
        
        print(f"🔍 Search results: {len(results)} chunks found (distance threshold: {distance_threshold})")
        if len(results) == 0:
            print("⚠️  No results found - consider increasing distance threshold")
            # Return top results even if above threshold
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.text_chunks):
                    results.append(self.text_chunks[idx])
                    if len(results) >= top_k:
                        break
        
        return results

    def get_stats(self):
        """Get statistics about the vector store"""
        return {
            'total_chunks': len(self.text_chunks),
            'dimension': self.dimension,
            'index_size': self.index.ntotal if hasattr(self.index, 'ntotal') else len(self.text_chunks)
        }
