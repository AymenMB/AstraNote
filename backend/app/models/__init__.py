"""
Import all models for easier access.
"""
from app.models.base import BaseModel
from app.models.user import User
from app.models.document import Document
from app.models.query import Query
from app.models.audit_log import AuditLog

__all__ = ["BaseModel", "User", "Document", "Query", "AuditLog"]
