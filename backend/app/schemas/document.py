"""
Document schemas for request/response serialization.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema."""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    pass


class DocumentUpdate(DocumentBase):
    """Schema for updating a document."""
    pass


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    content_preview: Optional[str]
    metadata: Optional[Dict[str, Any]]
    notebooklm_document_id: Optional[str]
    processing_status: str
    processing_error: Optional[str]
    query_count: int
    last_queried_at: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    """Schema for document upload response."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    processing_status: str
    message: str


class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status."""
    id: int
    filename: str
    processing_status: str
    processing_error: Optional[str]
    notebooklm_document_id: Optional[str]


class DocumentList(BaseModel):
    """Schema for document list response."""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentStats(BaseModel):
    """Schema for document statistics."""
    total_documents: int
    total_size: int
    by_file_type: Dict[str, int]
    by_status: Dict[str, int]
    recent_uploads: List[DocumentResponse]
