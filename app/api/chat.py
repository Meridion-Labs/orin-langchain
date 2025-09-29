"""Chat API endpoints."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel

from app.auth import verify_token, verify_api_key
from app.models import TokenData
from app.agents import create_agent_for_user
from app.rag import document_manager

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    context: Optional[Dict[str, Any]] = None


class SourceInfo(BaseModel):
    """Structured source metadata for RAG responses."""
    filename: str
    document_type: Optional[str] = None
    department: Optional[str] = None
    source: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    sources: Optional[List[SourceInfo]] = None
    success: bool
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    message: str
    document_id: List[str]
    success: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    token_data: TokenData = Depends(verify_token)
) -> ChatResponse:
    """Chat with the ORIN AI agent."""
    try:
        # Create user context
        user_context = {
            "user_id": token_data.email,
            "email": token_data.email,
            **(request.context or {})
        }
        
        # Create agent for user
        agent = create_agent_for_user(user_context)
        
        # Process query
        result = agent.query(request.message)
        
        # Debug logging
        print(f"DEBUG: Agent result: {result}")
        print(f"DEBUG: Sources from agent: {result.get('sources', [])}")
        
        return ChatResponse(
            response=result["response"],
            sources=result.get("sources", []),
            success=result["success"],
            metadata=result.get("metadata"),
            error=result.get("error")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/api-key")
async def chat_with_api_key(
    request: ChatRequest,
    api_key: str
) -> ChatResponse:
    """Chat endpoint for API key authentication."""
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    try:
        # Create minimal user context for API key users
        user_context = {
            "user_id": f"api_user_{api_key[:8]}",
            "api_key": True,
            **(request.context or {})
        }
        
        # Create agent for API user
        agent = create_agent_for_user(user_context)
        
        # Process query
        result = agent.query(request.message)
        
        return ChatResponse(
            response=result["response"],
            sources=result.get("sources", []),
            success=result["success"],
            metadata=result.get("metadata"),
            error=result.get("error")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    department: str = "general",
    document_type: str = "policy",
    token_data: TokenData = Depends(verify_token)
) -> DocumentUploadResponse:
    """Upload and index a document."""
    try:
        # Validate file type
        allowed_types = [".pdf", ".txt", ".doc", ".docx"]
        if not any(file.filename.endswith(ext) for ext in allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {allowed_types}"
            )
        
        # Save file temporarily
        import os
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Add document to vector store
            document_ids = document_manager.add_official_document(
                file_path=tmp_path,
                department=department,
                document_type=document_type
            )
            
            return DocumentUploadResponse(
                message=f"Document '{file.filename}' uploaded and indexed successfully",
                document_id=document_ids,
                success=True
            )
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )


@router.get("/documents/search")
async def search_documents(
    query: str,
    department: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 5,
    token_data: TokenData = Depends(verify_token)
):
    """Search through uploaded documents."""
    try:
        documents = document_manager.search_documents(
            query=query,
            k=limit,
            document_type=document_type,
            department=department
        )
        
        results = []
        for doc in documents:
            results.append({
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "metadata": doc.metadata
            })
        
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )