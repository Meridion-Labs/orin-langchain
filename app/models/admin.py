"""Admin models for document management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    filename: str
    department: str
    document_type: str
    size: int
    uploaded_by: str
    uploaded_at: datetime
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentUploadRequest(BaseModel):
    """Document upload request for admin."""
    department: str = "general"
    document_type: str = "policy"
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class BulkUploadResponse(BaseModel):
    """Bulk upload response model."""
    uploaded_files: List[str]
    failed_files: List[str]
    total_processed: int
    success_count: int
    error_count: int
    document_ids: List[str]


class DocumentSearchRequest(BaseModel):
    """Document search request."""
    query: Optional[str] = None
    department: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 10
    offset: int = 0


class DocumentDeleteRequest(BaseModel):
    """Document deletion request."""
    document_ids: List[str]
    reason: Optional[str] = None


class AdminDashboardStats(BaseModel):
    """Admin dashboard statistics."""
    total_documents: int
    documents_by_department: dict
    documents_by_type: dict
    recent_uploads: List[DocumentMetadata]
    storage_usage: dict


class UserManagementRequest(BaseModel):
    """User management request."""
    email: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str = "user"
    is_active: bool = True


class SystemConfigUpdate(BaseModel):
    """System configuration update."""
    key: str
    value: str
    description: Optional[str] = None