"""Main FastAPI application for ORIN AI Agent System."""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api import auth_router, chat_router

# Create FastAPI app
app = FastAPI(
    title="ORIN AI Agent System",
    description="AI agent for private/government offices to resolve queries and reduce staff coordination issues",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat & Documents"])


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "ORIN AI Agent System",
        "version": "1.0.0",
        "description": "AI agent for private/government offices",
        "features": [
            "RAG-based document search using Pinecone",
            "Secure user authentication with JWT",
            "Personalized data fetching from internal portals",
            "API key integration for platform connectivity",
            "Chat history management",
            "Multi-department support"
        ],
        "endpoints": {
            "authentication": "/auth",
            "chat": "/api/v1/chat",
            "documents": "/api/v1/documents",
            "api_docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )