"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, documents, queries, admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
