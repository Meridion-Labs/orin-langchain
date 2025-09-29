"""User models for authentication and authorization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str = "user"  # user, admin, staff
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model."""
    password: str


class User(UserBase):
    """User response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data for validation."""
    email: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class APIKey(BaseModel):
    """API Key model."""
    id: int
    key: str
    name: str
    user_id: int
    is_active: bool = True
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    """API Key creation model."""
    name: str
    expires_at: Optional[datetime] = None