"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model."""
    
    __tablename__ = "users"
    
    # Basic user information
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User status and permissions
    is_admin = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # NotebookLM integration
    notebook_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Profile information
    organization = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
