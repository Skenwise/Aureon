# schemas/userSchema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    Validates input data before passing to the service layer.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    All fields are optional; only provided fields are updated.
    """
    email: Optional[EmailStr] = Field(None, description="User's new email address")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    full_name: Optional[str] = Field(None, max_length=100, description="Updated full name")


class UserRead(BaseModel):
    """
    Schema for returning user data from the service or API layer.
    Sensitive fields like passwords are intentionally excluded.
    """
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # allows compatibility with ORM models
