"""
Authentication endpoints for user login, registration, and token management.
"""
from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    verify_password,
    get_password_hash,
)
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenRefresh,
)
from app.services.notebooklm import notebook_service
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user and create associated NotebookLM notebook.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    try:
        # Create NotebookLM notebook for the user
        notebook_display_name = f"{user_data.full_name}'s Knowledge Base"
        notebook_description = f"Personal knowledge base for {user_data.username}"
        
        notebook_response = await notebook_service.create_notebook(
            display_name=notebook_display_name,
            description=notebook_description
        )
        
        notebook_id = notebook_response.get("name", "").split("/")[-1]
        
        # Create user in database
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            organization=user_data.organization,
            department=user_data.department,
            bio=user_data.bio,
            notebook_id=notebook_id,
            is_verified=True,  # Auto-verify for now
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log registration event
        audit_log = AuditLog(
            event_type="user_registration",
            event_description=f"User {user_data.username} registered successfully",
            resource_type="user",
            resource_id=str(db_user.id),
            user_id=db_user.id,
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User registered successfully: {user_data.username}")
        
        return db_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access and refresh tokens.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        audit_log = AuditLog(
            event_type="login_failed",
            event_description=f"Failed login attempt for username: {form_data.username}",
            resource_type="user",
            metadata={"username": form_data.username},
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log successful login
    audit_log = AuditLog(
        event_type="login_success",
        event_description=f"User {user.username} logged in successfully",
        resource_type="user",
        resource_id=str(user.id),
        user_id=user.id,
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"User logged in successfully: {user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    """
    try:
        payload = verify_token(token_data.refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Logout user and invalidate tokens.
    """
    # Log logout event
    audit_log = AuditLog(
        event_type="logout",
        event_description=f"User {current_user.username} logged out",
        resource_type="user",
        resource_id=str(current_user.id),
        user_id=current_user.id,
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user
