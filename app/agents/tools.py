"""Tools for the ORIN AI Agent."""

import json
import httpx
from typing import Dict, Any, List
from langchain.tools import Tool
from langchain.schema import Document

from app.config import settings
from app.rag import document_manager


def search_documents(query: str, document_type: str = None, department: str = None) -> str:
    """Search through official documents and policies."""
    try:
        documents = document_manager.search_documents(
            query=query,
            k=3,
            document_type=document_type,
            department=department
        )
        
        if not documents:
            return "No relevant documents found for your query."
        
        results = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            metadata_info = ""
            if doc.metadata:
                metadata_info = f" [Source: {doc.metadata.get('source', 'Unknown')}]"
            results.append(f"{i}. {content}{metadata_info}")
        
        return "Relevant documents found:\n" + "\n\n".join(results)
    
    except Exception as e:
        return f"Error searching documents: {str(e)}"


def search_chat_history(query: str, user_id: str = None) -> str:
    """Search through previous chat conversations."""
    try:
        documents = document_manager.search_documents(
            query=query,
            k=2,
            document_type="chat_history",
            user_id=user_id
        )
        
        if not documents:
            return "No relevant chat history found."
        
        results = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            results.append(f"{i}. {content}")
        
        return "Previous relevant conversations:\n" + "\n\n".join(results)
    
    except Exception as e:
        return f"Error searching chat history: {str(e)}"


def fetch_user_data(user_id: str, data_type: str, auth_token: str = None) -> str:
    """Fetch personalized user data from internal portals (requires authentication)."""
    try:
        if not auth_token:
            return "Authentication required to access personalized data. Please provide valid credentials."
        
        if not settings.portal_base_url:
            return "Internal portal integration not configured."
        
        # Simulate API call to internal portal
        # In real implementation, this would make actual HTTP requests
        portal_url = f"{settings.portal_base_url}/api/user/{user_id}/{data_type}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "X-API-Key": settings.portal_api_key
        }
        
        # Placeholder response - in real implementation use httpx to make request
        # with httpx.Client() as client:
        #     response = client.get(portal_url, headers=headers)
        #     if response.status_code == 200:
        #         return json.dumps(response.json(), indent=2)
        
        # Mock data for demonstration
        mock_data = {
            "marks": {"Math": 85, "Science": 92, "English": 78},
            "attendance": {"total_days": 180, "present": 165, "percentage": 91.7},
            "profile": {"name": "John Doe", "id": user_id, "department": "Computer Science"}
        }
        
        if data_type in mock_data:
            return f"User data retrieved:\n{json.dumps(mock_data[data_type], indent=2)}"
        else:
            return f"Data type '{data_type}' not available."
    
    except Exception as e:
        return f"Error fetching user data: {str(e)}"


def create_api_response(data: Dict[str, Any]) -> str:
    """Format data for API response."""
    try:
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error formatting response: {str(e)}"


# Create Tool objects
search_documents_tool = Tool(
    name="search_documents",
    description="Search through official documents, policies, and procedures. Use this for general information queries.",
    func=search_documents
)

search_chat_history_tool = Tool(
    name="search_chat_history",
    description="Search through previous chat conversations to provide consistent responses and context.",
    func=search_chat_history
)

fetch_user_data_tool = Tool(
    name="fetch_user_data",
    description="Fetch personalized user data like marks, attendance, or profile information. Requires authentication.",
    func=fetch_user_data
)

create_api_response_tool = Tool(
    name="create_api_response",
    description="Format data into a structured API response format.",
    func=create_api_response
)