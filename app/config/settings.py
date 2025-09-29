"""Configuration settings for ORIN AI Agent System."""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Pinecone Configuration  
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "orin-documents"
    
    # Authentication
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    admin_emails: str = "admin@orin.ai"  # Comma-separated admin emails
    
    @field_validator('admin_emails')
    @classmethod
    def parse_admin_emails(cls, v) -> List[str]:
        """Parse comma-separated admin emails into a list."""
        if isinstance(v, str):
            return [email.strip() for email in v.split(',') if email.strip()]
        return v
    
    # Database
    database_url: str = "sqlite:///./orin.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Internal Portal Integration
    portal_base_url: str = ""
    portal_api_key: str = ""
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case insensitive matching
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance  
settings = Settings()