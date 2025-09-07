"""
Audit log model for compliance and monitoring.
"""
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Audit log model."""
    
    __tablename__ = "audit_logs"
    
    # Event information
    event_type = Column(String(100), nullable=False)  # login, logout, query, upload, delete, etc.
    event_description = Column(Text, nullable=False)
    resource_type = Column(String(100), nullable=True)  # user, document, query, etc.
    resource_id = Column(String(255), nullable=True)
    
    # Request information
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_params = Column(JSON, nullable=True)
    
    # Response information
    response_status = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    correlation_id = Column(String(255), index=True, nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id})>"
