"""
RAG system for FAQ retrieval and answering.
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.rag.vector_store import vector_store


class FAQRAG:
    """RAG system for clinic FAQ."""
    
    def __init__(self):
        """Initialize FAQ RAG system."""
        self.vector_store = vector_store
        self.clinic_data = self._load_clinic_data()
        
        # Initialize vector store if empty
        if self.vector_store.count() == 0:
            self._initialize_vector_store()
    
    def _load_clinic_data(self) -> Dict[str, Any]:
        """Load clinic information from JSON."""
        data_file = Path(__file__).parent.parent.parent / "data" / "clinic_info.json"
        with open(data_file, 'r') as f:
            return json.load(f)
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = ' > ') -> List[Dict[str, Any]]:
        """
        Flatten nested dictionary into list of documents.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            List of document dictionaries
        """
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep))
            elif isinstance(v, list):
                # Convert list to string
                content = "\n".join([str(item) for item in v])
                items.append({
                    "category": parent_key,
                    "topic": k,
                    "content": content,
                    "full_key": new_key
                })
            else:
                items.append({
                    "category": parent_key,
                    "topic": k,
                    "content": str(v),
                    "full_key": new_key
                })
        
        return items
    
    def _initialize_vector_store(self):
        """Initialize vector store with clinic data."""
        print("Initializing FAQ knowledge base...")
        
        documents = []
        metadatas = []
        ids = []
        
        # Flatten clinic data
        flattened_data = self._flatten_dict(self.clinic_data)
        
        for idx, item in enumerate(flattened_data):
            # Create document text
            doc_text = f"{item['topic']}: {item['content']}"
            
            documents.append(doc_text)
            metadatas.append({
                "category": item['category'],
                "topic": item['topic'],
                "full_key": item['full_key']
            })
            ids.append(f"doc_{idx}")
        
        # Add to vector store
        self.vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Initialized FAQ knowledge base with {len(documents)} documents")
    
    def retrieve_relevant_info(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information for a query.
        
        Args:
            query: User's question
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.vector_store.query(query, n_results=n_results)
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        
        return formatted_results
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and source documents
        """
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_info(question, n_results=3)
        
        # Compile context from relevant documents
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(doc['content'])
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": relevant_docs,
            "question": question
        }
    
    def get_specific_info(self, category: str, topic: Optional[str] = None) -> Optional[Any]:
        """
        Get specific information from clinic data.
        
        Args:
            category: Category (e.g., 'clinic_details', 'insurance_and_billing')
            topic: Specific topic within category
            
        Returns:
            The requested information
        """
        if category not in self.clinic_data:
            return None
        
        if topic is None:
            return self.clinic_data[category]
        
        return self.clinic_data[category].get(topic)
    
    def get_all_insurance_providers(self) -> List[str]:
        """Get list of accepted insurance providers."""
        return self.clinic_data.get("insurance_and_billing", {}).get("accepted_insurance", [])
    
    def get_appointment_types(self) -> Dict[str, Any]:
        """Get all appointment types with descriptions."""
        return self.clinic_data.get("appointment_types", {})
    
    def get_contact_info(self) -> Dict[str, str]:
        """Get contact information."""
        return self.clinic_data.get("contact_information", {})
    
    def get_policies(self) -> Dict[str, Any]:
        """Get all policies."""
        return self.clinic_data.get("policies", {})


# Global FAQ RAG instance
faq_rag = FAQRAG()

