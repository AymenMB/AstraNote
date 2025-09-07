"""
User management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate, PasswordChange

logger = structlog.get_logger()
router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.organization is not None:
        current_user.organization = profile_data.organization
    if profile_data.department is not None:
        current_user.department = profile_data.department
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
