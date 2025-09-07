"""
Query model for tracking user queries and responses.
"""
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Query(BaseModel):
    """Query model."""
    
    __tablename__ = "queries"
    
    # Query information
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), default="semantic", nullable=False)  # semantic, keyword, conversational
    
    # Response information
    response_text = Column(Text, nullable=True)
    response_sources = Column(JSON, nullable=True)  # List of source documents
    response_metadata = Column(JSON, nullable=True)
    
    # Query execution details
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    tokens_used = Column(Integer, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Context and conversation
    conversation_id = Column(String(255), index=True, nullable=True)
    parent_query_id = Column(Integer, ForeignKey("queries.id"), nullable=True)
    context = Column(JSON, nullable=True)  # Previous conversation context
    
    # Feedback and quality metrics
    user_rating = Column(Integer, nullable=True)  # 1-5 scale
    user_feedback = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="queries")
    
    # Self-referential relationship for conversation threading
    parent_query = relationship("Query", remote_side="Query.id", backref="child_queries")
    
    def __repr__(self):
        return f"<Query(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
