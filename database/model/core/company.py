# models/core/company.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from typing import Optional
from ..base import BaseModel

class Company(BaseModel, table=True):
    """
    Represents a tenant company in Aureon
    """
    code: str = Field(..., max_length=50, unique=True, index=True)
    name: str = Field(..., max_length=150)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    currency: Optional[str] = Field(default="USD", max_length=3)
    subscription_tier: Optional[str] = Field(default=None)
    subscription_status: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)