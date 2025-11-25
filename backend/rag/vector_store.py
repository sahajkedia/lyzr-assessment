"""
Vector store for FAQ documents using ChromaDB.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from backend.rag.embeddings import embedding_model


class VectorStore:
    """ChromaDB vector store for FAQ documents."""
    
    def __init__(self, collection_name: str = "clinic_faqs", persist_directory: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
        """
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent.parent.parent / "data" / "vectordb")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Clinic FAQ knowledge base"}
            )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique IDs
        """
        # Generate embeddings
        embeddings = embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            where: Filter conditions
            
        Returns:
            Query results with documents, metadatas, and distances
        """
        # Generate query embedding
        query_embedding = embedding_model.encode_single(query_text).tolist()
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(name=self.collection.name)
    
    def count(self) -> int:
        """Get number of documents in collection."""
        return self.collection.count()


# Global vector store instance
vector_store = VectorStore()

