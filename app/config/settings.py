"""Configuration settings for ORIN AI Agent System."""

import os
from typing import Optional

try:
    from decouple import config
except ImportError:
    # Fallback if decouple is not installed
    def config(key, default=None, cast=None):
        value = os.getenv(key, default)
        if cast and value is not None:
            return cast(value)
        return value

try:
    from pydantic import BaseSettings
except ImportError:
    # Fallback if pydantic is not available
    class BaseSettings:
        class Config:
            env_file = ".env"


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = config("OPENAI_API_KEY", default="")
    
    # Pinecone Configuration
    pinecone_api_key: str = config("PINECONE_API_KEY", default="")
    pinecone_environment: str = config("PINECONE_ENVIRONMENT", default="")
    pinecone_index_name: str = config("PINECONE_INDEX_NAME", default="orin-documents")
    
    # Authentication
    secret_key: str = config("SECRET_KEY", default="your-secret-key-here")
    algorithm: str = config("ALGORITHM", default="HS256")
    access_token_expire_minutes: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Database
    database_url: str = config("DATABASE_URL", default="sqlite:///./orin.db")
    
    # API Configuration
    api_host: str = config("API_HOST", default="0.0.0.0")
    api_port: int = config("API_PORT", default=8000, cast=int)
    debug: bool = config("DEBUG", default=True, cast=bool)
    
    # Internal Portal Integration
    portal_base_url: str = config("PORTAL_BASE_URL", default="")
    portal_api_key: str = config("PORTAL_API_KEY", default="")
    
    # File Storage
    upload_dir: str = config("UPLOAD_DIR", default="./uploads")
    max_file_size: int = config("MAX_FILE_SIZE", default=10485760, cast=int)
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()