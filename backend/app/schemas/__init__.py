"""
Import all schemas for easier access.
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    UserProfile,
    Token,
    TokenRefresh,
    PasswordChange,
)
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentUpload,
    DocumentProcessingStatus,
    DocumentList,
    DocumentStats,
)
from app.schemas.query import (
    QueryBase,
    QueryCreate,
    QueryUpdate,
    QueryResponse,
    QueryExecution,
    QueryResult,
    ConversationHistory,
    QueryStats,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "UserProfile",
    "Token",
    "TokenRefresh",
    "PasswordChange",
    # Document schemas
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentUpload",
    "DocumentProcessingStatus",
    "DocumentList",
    "DocumentStats",
    # Query schemas
    "QueryBase",
    "QueryCreate",
    "QueryUpdate",
    "QueryResponse",
    "QueryExecution",
    "QueryResult",
    "ConversationHistory",
    "QueryStats",
]
