# models/core/user.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional, List
from ..base import BaseModel
from .company import Company

class User(BaseModel, table=True):
    """
    Represents a user within a company (tenant)
    """
    username: str = Field(..., max_length=50, unique=True, index=True)
    email: str = Field(..., max_length=150, unique=True, index=True)
    hashed_password: str = Field(...)
    full_name: Optional[str] = Field(default=None, max_length=150)
    role: Optional[str] = Field(default="user", max_length=50)
    is_active: bool = Field(default=True)
    last_login: Optional[str] = Field(default=None)

    # Relationships
    company: Optional[Company] = Relationship(back_populates="users")