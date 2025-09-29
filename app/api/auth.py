"""Authentication API endpoints."""

from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import (
    authenticate_user,
    create_access_token,
    verify_token,
    generate_api_key,
    get_password_hash
)
from app.models import Token, UserLogin, User, UserCreate, APIKey, APIKeyCreate, TokenData
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user."""
    # This would typically check if user exists and create in database
    # For demo purposes, we'll return a mock user
    hashed_password = get_password_hash(user.password)
    
    return User(
        id=1,
        email=user.email,
        full_name=user.full_name,
        department=user.department,
        role=user.role,
        is_active=user.is_active,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )


@router.get("/profile", response_model=User)
async def get_profile(token_data: TokenData = Depends(verify_token)):
    """Get current user profile."""
    # This would fetch from database
    return User(
        id=1,
        email=token_data.email,
        full_name="John Doe",
        department="IT",
        role="user",
        is_active=True,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )


@router.post("/api-keys", response_model=APIKey)
async def create_api_key(
    api_key_data: APIKeyCreate,
    token_data: TokenData = Depends(verify_token)
):
    """Create a new API key for the user."""
    api_key = generate_api_key()
    
    # This would typically save to database
    return APIKey(
        id=1,
        key=api_key,
        name=api_key_data.name,
        user_id=1,  # Would get from token_data
        is_active=True,
        created_at="2024-01-01T00:00:00",
        expires_at=api_key_data.expires_at
    )


@router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys(token_data: TokenData = Depends(verify_token)):
    """List all API keys for the current user."""
    # This would fetch from database
    return [
        APIKey(
            id=1,
            key="orin_example_key_hidden",
            name="My API Key",
            user_id=1,
            is_active=True,
            created_at="2024-01-01T00:00:00",
            expires_at=None
        )
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    token_data: TokenData = Depends(verify_token)
):
    """Revoke an API key."""
    # This would update the database to deactivate the key
    return {"message": f"API key {key_id} has been revoked"}


@router.get("/verify")
async def verify_access(token_data: TokenData = Depends(verify_token)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user": token_data.email,
        "message": "Token is valid"
    }