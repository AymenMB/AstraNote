"""
Query endpoints for semantic search and conversation management.
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from sqlalchemy.orm import Session
import structlog
import time
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import cache_get, cache_set
from app.models.user import User
from app.models.query import Query
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.schemas.query import (
    QueryCreate,
    QueryResponse,
    QueryExecution,
    QueryResult,
    QueryUpdate,
    ConversationHistory,
    QueryStats,
)
from app.services.notebooklm import notebook_service

logger = structlog.get_logger()
router = APIRouter()


@router.post("/execute", response_model=QueryResult, status_code=status.HTTP_201_CREATED)
async def execute_query(
    query_data: QueryExecution,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Execute a semantic query against the user's NotebookLM notebook.
    """
    if not current_user.notebook_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a NotebookLM notebook"
        )
    
    try:
        # Generate conversation ID if not provided
        conversation_id = query_data.conversation_id or str(uuid.uuid4())
        
        # Check cache for similar recent queries
        cache_key = f"query:{current_user.id}:{hash(query_data.query_text)}"
        cached_result = await cache_get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for query: {query_data.query_text[:50]}...")
            return cached_result
        
        # Create query record
        query_record = Query(
            query_text=query_data.query_text,
            query_type="semantic",
            conversation_id=conversation_id,
            context=query_data.context,
            user_id=current_user.id,
            status="pending",
        )
        
        db.add(query_record)
        db.commit()
        db.refresh(query_record)
        
        start_time = time.time()
        
        try:
            # Execute query using NotebookLM
            result = await notebook_service.query_notebook(
                notebook_id=current_user.notebook_id,
                query=query_data.query_text,
                max_results=query_data.max_results,
                include_sources=query_data.include_sources,
                context=query_data.context,
            )
            
            execution_time = time.time() - start_time
            
            # Update query record with results
            query_record.response_text = result.get("answer", "")
            query_record.response_sources = result.get("sources", [])
            query_record.response_metadata = result.get("metadata", {})
            query_record.execution_time = execution_time
            query_record.status = "completed"
            
            # Update document query counts
            source_documents = result.get("sources", [])
            for source in source_documents:
                doc_id = source.get("document_id")
                if doc_id:
                    document = db.query(Document).filter(
                        Document.notebooklm_document_id == doc_id,
                        Document.owner_id == current_user.id
                    ).first()
                    if document:
                        document.query_count += 1
                        document.last_queried_at = query_record.created_at.isoformat()
            
            db.commit()
            
            # Prepare response
            query_result = QueryResult(
                query_id=query_record.id,
                query_text=query_data.query_text,
                response_text=result.get("answer", ""),
                sources=result.get("sources", []),
                metadata=result.get("metadata", {}),
                execution_time=execution_time,
                conversation_id=conversation_id,
                status="completed",
            )
            
            # Cache result
            await cache_set(cache_key, query_result.dict(), ttl=1800)  # 30 minutes
            
            # Log query event
            audit_log = AuditLog(
                event_type="query_execute",
                event_description=f"Query executed: {query_data.query_text[:100]}...",
                resource_type="query",
                resource_id=str(query_record.id),
                user_id=current_user.id,
                metadata={"execution_time": execution_time, "conversation_id": conversation_id},
            )
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Query executed successfully in {execution_time:.2f}s")
            
            return query_result
            
        except Exception as e:
            # Update query record with error
            query_record.status = "failed"
            query_record.error_message = str(e)
            query_record.execution_time = time.time() - start_time
            db.commit()
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute query"
        )


@router.get("", response_model=List[QueryResponse])
async def list_queries(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, ge=1, le=100),
    conversation_id: Optional[str] = QueryParam(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List user's queries with pagination and filtering.
    """
    query = db.query(Query).filter(Query.user_id == current_user.id)
    
    if conversation_id:
        query = query.filter(Query.conversation_id == conversation_id)
    
    queries = query.order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    
    return queries


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get query by ID.
    """
    query = db.query(Query).filter(
        Query.id == query_id,
        Query.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    return query


@router.put("/{query_id}/feedback", response_model=QueryResponse)
async def update_query_feedback(
    query_id: int,
    feedback_data: QueryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update query feedback (rating and comments).
    """
    query = db.query(Query).filter(
        Query.id == query_id,
        Query.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Update feedback fields
    if feedback_data.user_rating is not None:
        query.user_rating = feedback_data.user_rating
    if feedback_data.user_feedback is not None:
        query.user_feedback = feedback_data.user_feedback
    
    db.commit()
    db.refresh(query)
    
    # Log feedback event
    audit_log = AuditLog(
        event_type="query_feedback",
        event_description=f"Query feedback updated: rating={feedback_data.user_rating}",
        resource_type="query",
        resource_id=str(query.id),
        user_id=current_user.id,
    )
    db.add(audit_log)
    db.commit()
    
    return query


@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get conversation history by conversation ID.
    """
    queries = db.query(Query).filter(
        Query.conversation_id == conversation_id,
        Query.user_id == current_user.id
    ).order_by(Query.created_at.asc()).all()
    
    if not queries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationHistory(
        conversation_id=conversation_id,
        queries=queries,
        total_queries=len(queries),
        started_at=queries[0].created_at,
        last_activity=queries[-1].created_at,
    )


@router.get("/stats/overview", response_model=QueryStats)
async def get_query_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get query statistics for the user.
    """
    # Get all user queries
    queries = db.query(Query).filter(Query.user_id == current_user.id).all()
    
    total_queries = len(queries)
    successful_queries = len([q for q in queries if q.status == "completed"])
    failed_queries = len([q for q in queries if q.status == "failed"])
    
    # Calculate average execution time
    execution_times = [q.execution_time for q in queries if q.execution_time is not None]
    average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    # Calculate average rating
    ratings = [q.user_rating for q in queries if q.user_rating is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else None
    
    # Get popular queries (most common query texts)
    query_texts = [q.query_text for q in queries]
    popular_queries = list(set(query_texts))[:10]  # Simple implementation
    
    # Get recent queries
    recent_queries = db.query(Query).filter(
        Query.user_id == current_user.id
    ).order_by(Query.created_at.desc()).limit(10).all()
    
    return QueryStats(
        total_queries=total_queries,
        successful_queries=successful_queries,
        failed_queries=failed_queries,
        average_execution_time=average_execution_time,
        average_rating=average_rating,
        popular_queries=popular_queries,
        recent_queries=recent_queries,
    )
