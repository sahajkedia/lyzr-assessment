"""
Embeddings generation for RAG system.
"""
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingModel:
    """Wrapper for embedding model."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string
            
        Returns:
            Numpy array embedding
        """
        return self.encode([text])[0]


# Global embedding model instance
embedding_model = EmbeddingModel()

