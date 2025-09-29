"""Vector store management using Pinecone."""

import os
from typing import List, Dict, Any, Optional
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document

from app.config import settings


class VectorStore:
    """Manages vector store operations with Pinecone."""
    
    def __init__(self):
        """Initialize Pinecone vector store."""
        self.embeddings = None
        self.vectorstore = None
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection."""
        try:
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
            
            # Check if index exists, create if not
            if settings.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.pinecone_index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            # Initialize vectorstore
            self.vectorstore = Pinecone.from_existing_index(
                index_name=settings.pinecone_index_name,
                embedding=self.embeddings
            )
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            # Fallback to local storage if Pinecone fails
            self.vectorstore = None
    
    def add_documents(self, documents: List[Document], metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Add documents to the vector store."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        # Add metadata to documents
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)
        
        # Add to vector store
        ids = self.vectorstore.add_documents(splits)
        return ids
    
    def similarity_search(self, query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search for similar documents."""
        if not self.vectorstore:
            return []
        
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Search for similar documents with relevance scores."""
        if not self.vectorstore:
            return []
        
        return self.vectorstore.similarity_search_with_score(query=query, k=k)
    
    def delete_documents(self, ids: List[str]):
        """Delete documents by IDs."""
        if not self.vectorstore:
            return
        
        # Note: Pinecone deletion would need to be implemented based on metadata
        # This is a placeholder for the deletion logic
        pass
    
    def load_and_add_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Load a file and add it to the vector store."""
        documents = []
        
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        return self.add_documents(documents, metadata)


# Global vector store instance
vector_store = VectorStore()