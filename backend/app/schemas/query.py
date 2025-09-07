"""
Query schemas for request/response serialization.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class QueryBase(BaseModel):
    """Base query schema."""
    query_text: str = Field(..., min_length=1, max_length=4000)
    query_type: str = Field(default="semantic", regex="^(semantic|keyword|conversational)$")


class QueryCreate(QueryBase):
    """Schema for creating a query."""
    conversation_id: Optional[str] = None
    parent_query_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class QueryUpdate(BaseModel):
    """Schema for updating a query."""
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = Field(None, max_length=2000)


class QueryResponse(QueryBase):
    """Schema for query response."""
    id: int
    response_text: Optional[str]
    response_sources: Optional[List[Dict[str, Any]]]
    response_metadata: Optional[Dict[str, Any]]
    execution_time: Optional[float]
    tokens_used: Optional[int]
    status: str
    error_message: Optional[str]
    conversation_id: Optional[str]
    parent_query_id: Optional[int]
    context: Optional[Dict[str, Any]]
    user_rating: Optional[int]
    user_feedback: Optional[str]
    relevance_score: Optional[float]
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QueryExecution(BaseModel):
    """Schema for query execution request."""
    query_text: str = Field(..., min_length=1, max_length=4000)
    include_sources: bool = Field(default=True)
    max_results: int = Field(default=10, ge=1, le=50)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    """Schema for query execution result."""
    query_id: int
    query_text: str
    response_text: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float
    conversation_id: Optional[str]
    status: str


class ConversationHistory(BaseModel):
    """Schema for conversation history."""
    conversation_id: str
    queries: List[QueryResponse]
    total_queries: int
    started_at: datetime
    last_activity: datetime


class QueryStats(BaseModel):
    """Schema for query statistics."""
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_execution_time: float
    average_rating: Optional[float]
    popular_queries: List[str]
    recent_queries: List[QueryResponse]
