"""Authentication utilities."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models import TokenData

# Password hashing context - using simple PBKDF2 for development
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT token security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Verify JWT token and return token data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    return token_data


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Verify JWT token and ensure user has admin role."""
    token_data = verify_token(credentials)
    
    # For now, we'll use a simple email-based admin check
    # In production, this should check against a database
    admin_emails = settings.admin_emails or ["admin@orin.ai"]
    
    if token_data.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return token_data


# Simple in-memory user store for demo purposes
# In production, this would be replaced with a proper database
fake_users_db = {}


def initialize_demo_users():
    """Initialize some demo users."""
    global fake_users_db
    if not fake_users_db:  # Only initialize if empty
        fake_users_db.update({
            "test@example.com": {
                "email": "test@example.com",
                "full_name": "Test User",
                "hashed_password": get_password_hash("testpassword"),
                "department": "IT",
                "role": "user",
                "is_active": True
            },
            "admin@example.com": {
                "email": "admin@example.com", 
                "full_name": "Admin User",
                "hashed_password": get_password_hash("adminpassword"),
                "department": "Administration",
                "role": "admin",
                "is_active": True
            },
            "chambyal20062003@gmail.com": {
                "email": "chambyal20062003@gmail.com", 
                "full_name": "Admin User",
                "hashed_password": get_password_hash("admin123"),
                "department": "Administration",
                "role": "admin",
                "is_active": True
            }
        })


def get_user(email: str):
    """Get user from database."""
    if not fake_users_db:  # Initialize if empty
        initialize_demo_users()
    return fake_users_db.get(email)


def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user against stored credentials."""
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_user(email: str, password: str, full_name: str = None, department: str = None):
    """Create a new user (for demo purposes)."""
    if not fake_users_db:  # Initialize if empty
        initialize_demo_users()
        
    if email in fake_users_db:
        return False  # User already exists
    
    fake_users_db[email] = {
        "email": email,
        "full_name": full_name or email.split("@")[0],
        "hashed_password": get_password_hash(password),
        "department": department or "General",
        "role": "user",
        "is_active": True
    }
    return True


def generate_api_key() -> str:
    """Generate a new API key."""
    import secrets
    return f"orin_{''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))}"


def verify_api_key(api_key: str) -> bool:
    """Verify API key (placeholder for database integration)."""
    # This would check against your API keys database
    return api_key.startswith("orin_")