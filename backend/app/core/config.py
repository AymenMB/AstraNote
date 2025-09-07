"""
Application configuration settings.
"""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic configuration
    PROJECT_NAME: str = "NotebookLM RAG System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database configuration
    DATABASE_URL: str
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Google Cloud configuration
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_CLOUD_PROJECT: str
    NOTEBOOKLM_API_KEY: str
    
    # Security configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Allowed hosts for security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # File upload configuration
    MAX_UPLOAD_SIZE: int = 50000000  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "html"]
    UPLOAD_DIRECTORY: str = "./uploads"
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    
    # Email configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Cache configuration
    CACHE_TTL: int = 3600  # 1 hour
    QUERY_CACHE_TTL: int = 1800  # 30 minutes
    
    # NotebookLM specific settings
    NOTEBOOKLM_API_BASE_URL: str = "https://notebooks.googleapis.com/v1"
    NOTEBOOKLM_MAX_DOCUMENTS: int = 50
    NOTEBOOKLM_MAX_QUERY_LENGTH: int = 4000
    NOTEBOOKLM_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)
