"""
Vector store service using FAISS for document embeddings and similarity search.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
import faiss
from langchain_openai import AzureOpenAIEmbeddings

from app.core.config import settings
from app.services.local_embeddings import LocalEmbeddings


class VectorStore:
    """FAISS-based vector store for document embeddings."""
    
    def __init__(self, use_local_embeddings: bool = True):
        """
        Initialize the vector store.
        
        Args:
            use_local_embeddings: If True, use local embeddings. If False, try Azure OpenAI.
        """
        self.embeddings = None
        self.embedding_type = "none"
        
        if use_local_embeddings:
            # Try to use local embeddings first
            try:
                self.embeddings = LocalEmbeddings()
                self.embedding_type = "local"
                self.dimension = self.embeddings.get_dimension()
                print(f"✅ Using local embeddings (dimension: {self.dimension})")
            except Exception as e:
                print(f"⚠️  Failed to load local embeddings: {e}")
                print("🔄 Falling back to Azure OpenAI...")
                use_local_embeddings = False
        
        if not use_local_embeddings:
            # Try Azure OpenAI embeddings
            if (settings.azure_openai_api_key and 
                settings.azure_openai_endpoint ):
                try:
                    self.embeddings = AzureOpenAIEmbeddings(
                        azure_endpoint=settings.azure_openai_endpoint,
                        api_key=settings.azure_openai_api_key,
                        api_version=settings.azure_openai_api_version,
                        azure_deployment="text-embedding-ada-002"  # Default embedding model
                    )
                    # Test the connection with a simple embedding
                    test_embedding = self.embeddings.embed_query("test")
                    self.embedding_type = "azure"
                    self.dimension = 1536  # OpenAI embedding dimension
                    print("✅ Azure OpenAI embeddings configured successfully")
                except Exception as e:
                    print(f"⚠️  Azure OpenAI connection failed: {e}")
                    self.embeddings = None
            else:
                print("⚠️  Azure OpenAI not configured.")
        
        if self.embeddings is None:
            print("❌ No embedding service available. Vector store will work in limited mode.")
            self.dimension = 384  # Default dimension
        
        self.index_file = os.path.join(settings.vector_store_dir, "faiss_index.bin")
        self.metadata_file = os.path.join(settings.vector_store_dir, "metadata.pkl")
        
        self.index = None
        self.metadata = []
        
        self._load_or_create_index()
    
    def _load_or_create_index(self) -> None:
        """Load existing index or create a new one."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                print(f"Loaded existing vector store with {len(self.metadata)} documents")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("Created new vector store")
    
    def _save_index(self) -> None:
        """Save the FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, self.index_file)
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def add_documents(self, chunks: List[str], document_id: str, filename: str) -> None:
        """Add document chunks to the vector store."""
        if not self.embeddings:
            raise ValueError("No embedding service available. Cannot add documents to vector store.")
        
        try:
            # Generate embeddings for chunks
            embeddings = self.embeddings.embed_documents(chunks)
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": i,
                    "text": chunk,
                    "vector_id": len(self.metadata)  # Current position in index
                }
                self.metadata.append(chunk_metadata)
            
            # Save to disk
            self._save_index()
            
            print(f"Added {len(chunks)} chunks from {filename} to vector store")
            
        except Exception as e:
            raise ValueError(f"Error adding documents to vector store: {str(e)}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search and return relevant chunks."""
        if not self.embeddings:
            print("⚠️  No embedding service available. Cannot perform similarity search.")
            return []
        
        if self.index.ntotal == 0:
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Retrieve metadata for found chunks
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result["similarity_score"] = float(distance)
                    result["rank"] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []
    
    def remove_document(self, document_id: str) -> bool:
        """Remove all chunks of a document from the vector store."""
        try:
            # Find indices of chunks belonging to the document
            indices_to_remove = []
            for i, metadata in enumerate(self.metadata):
                if metadata["document_id"] == document_id:
                    indices_to_remove.append(i)
            
            if not indices_to_remove:
                return False
            
            # Remove from metadata (in reverse order to maintain indices)
            for idx in reversed(indices_to_remove):
                del self.metadata[idx]
            
            # Rebuild the FAISS index (FAISS doesn't support efficient deletion)
            if self.metadata:
                # Get all remaining embeddings
                remaining_texts = [meta["text"] for meta in self.metadata]
                embeddings = self.embeddings.embed_documents(remaining_texts)
                embeddings_array = np.array(embeddings, dtype=np.float32)
                
                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.index.add(embeddings_array)
                
                # Update vector_ids in metadata
                for i, meta in enumerate(self.metadata):
                    meta["vector_id"] = i
            else:
                # Create empty index if no documents remain
                self.index = faiss.IndexFlatL2(self.dimension)
            
            # Save updated index
            self._save_index()
            
            print(f"Removed document {document_id} from vector store")
            return True
            
        except Exception as e:
            print(f"Error removing document from vector store: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        document_ids = set()
        for meta in self.metadata:
            document_ids.add(meta["document_id"])
        
        return {
            "total_chunks": len(self.metadata),
            "total_documents": len(document_ids),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension
        }
    
    def clear_all(self) -> None:
        """Clear all data from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self._save_index()
        print("Cleared all data from vector store") 