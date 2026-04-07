# API/schemas/auth.py
"""
Authentication API Schemas.

API-specific request and response models for authentication endpoints.
These are separate from domain schemas to maintain layer isolation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class LoginRequest(BaseModel):
    """
    Login request schema.
    
    Sent by client to authenticate a user.
    """
    username: str = Field(..., description="User's unique username", min_length=3, max_length=50)
    password: str = Field(..., description="User's password", min_length=1)


class RegisterRequest(BaseModel):
    """
    Registration request schema.
    
    Sent by client to create a new user account.
    
    DEV ONLY: In production, user creation is restricted to Admins after KYC verification.
    This endpoint exists for development and testing purposes only.
    """
    username: str = Field(..., description="Unique username", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="Password", min_length=8)
    full_name: Optional[str] = Field(None, description="User's full name", max_length=100)


class TokenResponse(BaseModel):
    """
    Token response schema.
    
    Returned to client after successful authentication.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(default=900, description="Token expiration in seconds (15 minutes)")


class RegisterResponse(BaseModel):
    """
    Registration response schema.
    
    Returns the created user information (excluding password).
    """
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True