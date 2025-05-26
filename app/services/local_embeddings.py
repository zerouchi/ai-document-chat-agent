"""
Local embeddings service using sentence-transformers.
Provides a lightweight alternative to Azure OpenAI embeddings.
"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class LocalEmbeddings:
    """Local embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the local embeddings model.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is 'all-MiniLM-L6-v2' which is lightweight and fast.
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            print(f"🤖 Loading local embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Local embedding model loaded successfully")
            
            # Update dimension based on the actual model
            test_embedding = self.model.encode("test")
            self.dimension = len(test_embedding)
            print(f"📏 Embedding dimension: {self.dimension}")
            
        except Exception as e:
            print(f"❌ Failed to load local embedding model: {e}")
            raise e
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text documents to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not self.model:
            raise ValueError("Local embedding model not loaded")
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Convert to list of lists for compatibility
            return embeddings.tolist()
            
        except Exception as e:
            raise ValueError(f"Error generating document embeddings: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding as a list of floats
        """
        if not self.model:
            raise ValueError("Local embedding model not loaded")
        
        try:
            # Generate embedding
            embedding = self.model.encode([text], convert_to_numpy=True)
            
            # Return as list for compatibility
            return embedding[0].tolist()
            
        except Exception as e:
            raise ValueError(f"Error generating query embedding: {str(e)}")
    
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.dimension


# Available models with their characteristics
AVAILABLE_MODELS = {
    "all-MiniLM-L6-v2": {
        "dimension": 384,
        "description": "Lightweight and fast, good for most use cases",
        "size": "~80MB"
    },
    "all-mpnet-base-v2": {
        "dimension": 768,
        "description": "Higher quality embeddings, larger model",
        "size": "~420MB"
    },
    "paraphrase-MiniLM-L6-v2": {
        "dimension": 384,
        "description": "Optimized for paraphrase detection",
        "size": "~80MB"
    },
    "distilbert-base-nli-mean-tokens": {
        "dimension": 768,
        "description": "Based on DistilBERT, good performance",
        "size": "~250MB"
    }
}


def get_available_models():
    """Get information about available embedding models."""
    return AVAILABLE_MODELS


def create_local_embeddings(model_name: str = "all-MiniLM-L6-v2") -> LocalEmbeddings:
    """
    Create a local embeddings instance.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        LocalEmbeddings instance
    """
    return LocalEmbeddings(model_name=model_name) 