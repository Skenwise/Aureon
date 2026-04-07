# schemas/tenants.py
from sqlmodel import SQLModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class TenantCreate(SQLModel):
    """
    Schema for creating a new tenant (Company).
    """
    code: str
    name: str
    timezone: Optional[str] = "UTC"
    currency: Optional[str] = "USD"
    subscription_tier: Optional[str] = None
    subscription_status: Optional[str] = None
    note: Optional[str] = None


class TenantUpdate(SQLModel):
    """
    Schema for updating an existing tenant (Company).
    All fields are optional to allow partial updates.
    """
    code: Optional[str] = None
    name: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    subscription_tier: Optional[str] = None
    subscription_status: Optional[str] = None
    note: Optional[str] = None


class TenantRead(SQLModel):
    """
    Schema for reading tenant data. Separate from Company model for API safety.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    code: str
    name: str
    timezone: Optional[str]
    currency: Optional[str]
    subscription_tier: Optional[str]
    subscription_status: Optional[str]
    note: Optional[str]