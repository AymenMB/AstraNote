"""
Document management endpoints for upload, processing, and retrieval.
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query as QueryParam
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.schemas.document import (
    DocumentResponse,
    DocumentUpload,
    DocumentUpdate,
    DocumentList,
    DocumentProcessingStatus,
    DocumentStats,
)
from app.services.document_processor import document_processor
from app.services.notebooklm import notebook_service

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=DocumentUpload, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload a document and process it for NotebookLM.
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file
        is_valid, error_message = document_processor.validate_file(file_content, file.filename)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Save file to disk
        file_path, generated_filename = document_processor.save_file(
            file_content, file.filename, current_user.id
        )
        
        # Extract file type
        file_type = file.filename.split('.')[-1].lower()
        
        # Create document record
        document = Document(
            filename=generated_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            file_type=file_type,
            mime_type=file.content_type or "application/octet-stream",
            title=title or file.filename,
            description=description,
            owner_id=current_user.id,
            processing_status="pending",
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Log upload event
        audit_log = AuditLog(
            event_type="document_upload",
            event_description=f"Document uploaded: {file.filename}",
            resource_type="document",
            resource_id=str(document.id),
            user_id=current_user.id,
            metadata={"filename": file.filename, "file_size": len(file_content)},
        )
        db.add(audit_log)
        db.commit()
        
        # Start background processing
        # In a real implementation, this would be done via Celery or similar
        await process_document_async(document.id, db)
        
        logger.info(f"Document uploaded: {file.filename} by user {current_user.username}")
        
        return DocumentUpload(
            id=document.id,
            filename=generated_filename,
            original_filename=file.filename,
            file_size=len(file_content),
            processing_status="pending",
            message="Document uploaded successfully and is being processed",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


async def process_document_async(document_id: int, db: Session):
    """
    Process document asynchronously (in a real app, this would be a Celery task).
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        # Update status to processing
        document.processing_status = "processing"
        db.commit()
        
        # Extract content
        content, metadata = document_processor.extract_content(
            document.file_path, document.file_type
        )
        
        # Generate content preview
        content_preview = document_processor.get_content_preview(content)
        
        # Upload to NotebookLM
        user = db.query(User).filter(User.id == document.owner_id).first()
        if user and user.notebook_id:
            with open(document.file_path, 'rb') as f:
                file_content = f.read()
            
            notebook_response = await notebook_service.upload_document(
                notebook_id=user.notebook_id,
                file_content=file_content,
                filename=document.original_filename,
                mime_type=document.mime_type
            )
            
            notebooklm_document_id = notebook_response.get("name", "").split("/")[-1]
            
            # Update document with processing results
            document.content_preview = content_preview
            document.metadata = metadata
            document.notebooklm_document_id = notebooklm_document_id
            document.processing_status = "completed"
        else:
            document.processing_status = "failed"
            document.processing_error = "User notebook not found"
        
        db.commit()
        
    except Exception as e:
        # Update status to failed
        document.processing_status = "failed"
        document.processing_error = str(e)
        db.commit()
        logger.error(f"Error processing document {document_id}: {e}")


@router.get("", response_model=DocumentList)
async def list_documents(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=100),
    status_filter: Optional[str] = QueryParam(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List user's documents with pagination and filtering.
    """
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    
    if status_filter:
        query = query.filter(Document.processing_status == status_filter)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    return DocumentList(
        documents=documents,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get document by ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update document metadata.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    if document_update.title is not None:
        document.title = document_update.title
    if document_update.description is not None:
        document.description = document_update.description
    
    db.commit()
    db.refresh(document)
    
    # Log update event
    audit_log = AuditLog(
        event_type="document_update",
        event_description=f"Document updated: {document.original_filename}",
        resource_type="document",
        resource_id=str(document.id),
        user_id=current_user.id,
    )
    db.add(audit_log)
    db.commit()
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        # Delete from NotebookLM if it exists
        if document.notebooklm_document_id and current_user.notebook_id:
            await notebook_service.delete_document(
                current_user.notebook_id,
                document.notebooklm_document_id
            )
        
        # Delete file from disk
        document_processor.delete_file(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        # Log deletion event
        audit_log = AuditLog(
            event_type="document_delete",
            event_description=f"Document deleted: {document.original_filename}",
            resource_type="document",
            resource_id=str(document.id),
            user_id=current_user.id,
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Document deleted: {document.original_filename} by user {current_user.username}")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_document_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get document processing status.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentProcessingStatus(
        id=document.id,
        filename=document.original_filename,
        processing_status=document.processing_status,
        processing_error=document.processing_error,
        notebooklm_document_id=document.notebooklm_document_id,
    )


@router.get("/stats/overview", response_model=DocumentStats)
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get document statistics for the user.
    """
    # Get all user documents
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    
    # Calculate statistics
    total_documents = len(documents)
    total_size = sum(doc.file_size for doc in documents)
    
    # Group by file type
    by_file_type = {}
    for doc in documents:
        by_file_type[doc.file_type] = by_file_type.get(doc.file_type, 0) + 1
    
    # Group by status
    by_status = {}
    for doc in documents:
        by_status[doc.processing_status] = by_status.get(doc.processing_status, 0) + 1
    
    # Get recent uploads (last 10)
    recent_uploads = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).order_by(Document.created_at.desc()).limit(10).all()
    
    return DocumentStats(
        total_documents=total_documents,
        total_size=total_size,
        by_file_type=by_file_type,
        by_status=by_status,
        recent_uploads=recent_uploads,
    )
