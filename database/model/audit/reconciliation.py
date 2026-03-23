# models/audit/reconciliation.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from pydantic import field_validator
from ..base import BaseModel


class Reconciliation(BaseModel, table=True):
    """
    Daily ledger reconciliation snapshot.
    Proves the system was balanced at a given point in time.
    """
    
    # Tenant isolation — CRITICAL for multi-tenancy
    tenant_id: UUID = Field(foreign_key="company.id", nullable=False, index=True)
    
    business_date: date = Field(index=True)
    reconciliation_number: str = Field(..., max_length=50, unique=True, index=True)

    total_debits: int = Field(..., ge=0)
    total_credits: int = Field(..., ge=0)

    balanced: bool = Field(index=True)

    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_by: Optional[UUID] = Field(foreign_key="user.id", default=None)
    notes: Optional[str] = Field(default=None, max_length=500)

    # ==================== VALIDATORS ====================

    @field_validator('total_debits', mode='before')
    @classmethod
    def validate_total_debits(cls, v):
        if v is None:
            raise ValueError("Total debits cannot be None")
        if v < 0:
            raise ValueError("Total debits cannot be negative")
        return v

    @field_validator('total_credits', mode='before')
    @classmethod
    def validate_total_credits(cls, v):
        if v is None:
            raise ValueError("Total credits cannot be None")
        if v < 0:
            raise ValueError("Total credits cannot be negative")
        return v

    @field_validator('balanced', mode='before')
    @classmethod
    def validate_balanced(cls, v, info):
        if v is not None:
            return v
        values = info.data
        debits = values.get('total_debits', 0)
        credits = values.get('total_credits', 0)
        return debits == credits