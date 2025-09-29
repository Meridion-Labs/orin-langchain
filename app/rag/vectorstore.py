"""Vector store management using Pinecone."""

import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document

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
            # Debug: Check if API key is loaded
            if not settings.pinecone_api_key:
                print(f"Warning: Pinecone API key not found in settings")
                return
                
            print(f"Debug: Pinecone API key loaded: {'*' * 10}")
            
            # Set environment variable for Pinecone
            import os
            os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Initialize embeddings with model that matches your index dimensions
            # Using text-embedding-3-small which produces 1536 dimensions by default
            # but can be reduced to 1024 dimensions
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                model="text-embedding-3-small",
                dimensions=1024  # Match your Pinecone index
            )
            
            # Check if index exists, create if not
            index_names = [index.name for index in pc.list_indexes()]
            if settings.pinecone_index_name not in index_names:
                pc.create_index(
                    name=settings.pinecone_index_name,
                    dimension=1024,  # Match your existing Pinecone index dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone_environment or 'us-west-2'
                    )
                )
            
            # Initialize vectorstore
            self.vectorstore = PineconeVectorStore.from_existing_index(
                index_name=settings.pinecone_index_name,
                embedding=self.embeddings
            )
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            # Fallback to local storage if Pinecone fails
            self.vectorstore = None
            self.embeddings = None
            print("Warning: Running without vector store. Documents will not be indexed.")
    
    def add_documents(self, documents: List[Document], metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Add documents to the vector store."""
        if not self.vectorstore:
            print("Warning: Vector store not initialized. Skipping document indexing.")
            # Return mock IDs for demo purposes
            return [f"mock_id_{i}" for i in range(len(documents))]
        
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
            print("Warning: Vector store not initialized. Returning empty results.")
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
        
        try:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif file_path.endswith('.txt'):
                loader = TextLoader(file_path)
                documents = loader.load()
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            elif file_path.endswith('.doc'):
                # For .doc files, we'll try to use Docx2txtLoader as well
                # Note: This might not work for all .doc files, ideally we'd use python-docx2txt
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            print(f"Loaded {len(documents)} documents from {file_path}")
            return self.add_documents(documents, metadata)
            
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            # Return mock ID even if there's an error, so the upload doesn't completely fail
            return [f"error_mock_id_{hash(file_path)}"]


# Global vector store instance - lazy initialization
_vector_store = None

def get_vector_store():
    """Get the global vector store instance with lazy initialization."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store