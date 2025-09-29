"""Document retrieval system for RAG."""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.retrievers import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun

from .vectorstore import vector_store


class ORINRetriever(BaseRetriever):
    """Custom retriever for ORIN system with filtering capabilities."""
    
    def __init__(self, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None):
        """Initialize retriever."""
        super().__init__()
        self.k = k
        self.filter_dict = filter_dict or {}
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get relevant documents for the query."""
        return vector_store.similarity_search(
            query=query,
            k=self.k,
            filter_dict=self.filter_dict
        )


class DocumentManager:
    """Manages document operations for the RAG system."""
    
    @staticmethod
    def add_document(content: str, metadata: Dict[str, Any]) -> List[str]:
        """Add a single document to the vector store."""
        doc = Document(page_content=content, metadata=metadata)
        return vector_store.add_documents([doc])
    
    @staticmethod
    def add_chat_history(user_query: str, ai_response: str, user_id: str, department: str = None) -> List[str]:
        """Add chat history to the vector store for future reference."""
        chat_content = f"User Query: {user_query}\nAI Response: {ai_response}"
        metadata = {
            "type": "chat_history",
            "user_id": user_id,
            "department": department,
            "timestamp": str(vector_store.embeddings.client._get_current_time() if hasattr(vector_store.embeddings, 'client') else "")
        }
        return DocumentManager.add_document(chat_content, metadata)
    
    @staticmethod
    def search_documents(
        query: str, 
        k: int = 5, 
        document_type: Optional[str] = None,
        department: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Document]:
        """Search documents with optional filtering."""
        filter_dict = {}
        
        if document_type:
            filter_dict["type"] = document_type
        if department:
            filter_dict["department"] = department
        if user_id:
            filter_dict["user_id"] = user_id
        
        return vector_store.similarity_search(
            query=query,
            k=k,
            filter_dict=filter_dict if filter_dict else None
        )
    
    @staticmethod
    def search_with_scores(query: str, k: int = 5) -> List[tuple]:
        """Search documents with relevance scores."""
        return vector_store.similarity_search_with_score(query=query, k=k)
    
    @staticmethod
    def add_official_document(file_path: str, department: str, document_type: str) -> List[str]:
        """Add an official document to the vector store."""
        metadata = {
            "type": "official_document",
            "document_type": document_type,
            "department": department,
            "source": file_path
        }
        return vector_store.load_and_add_file(file_path, metadata)


# Global document manager instance
document_manager = DocumentManager()