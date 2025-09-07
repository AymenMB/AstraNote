"""
Document model for managing uploaded documents.
"""
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Document(BaseModel):
    """Document model."""
    
    __tablename__ = "documents"
    
    # Basic document information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Document content and metadata
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    content_preview = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # NotebookLM integration
    notebooklm_document_id = Column(String(255), unique=True, index=True, nullable=True)
    processing_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    
    # Document statistics
    query_count = Column(Integer, default=0, nullable=False)
    last_queried_at = Column(String(255), nullable=True)  # ISO datetime string
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', owner_id={self.owner_id})>"
