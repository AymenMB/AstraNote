"""
Admin endpoints for system management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User
from app.models.document import Document
from app.models.query import Query
from app.models.audit_log import AuditLog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/stats/system")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_documents = db.query(Document).count()
    total_queries = db.query(Query).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_documents": total_documents,
        "total_queries": total_queries,
    }


@router.get("/users")
async def list_all_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users


@router.get("/audit-logs")
async def get_audit_logs(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return logs
