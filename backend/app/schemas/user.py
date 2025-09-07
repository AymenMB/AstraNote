"""
User schemas for request/response serialization.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    organization: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    organization: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_admin: bool
    is_verified: bool
    notebook_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserProfile(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    email: str
    full_name: str
    organization: Optional[str]
    department: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    notebook_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
