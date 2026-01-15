# models/audit/reconciliation.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from ..base import BaseModel

class Reconciliation(BaseModel, table=True):
    """
    Daily ledger reconciliation snapshot.
    Proves the system was balanced at a given point in time.
    """
    business_date: date = Field(index=True)

    total_debits: int
    total_credits: int

    balanced: bool = Field(index=True)

    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    calculated_by: Optional[UUID] = Field(
        foreign_key="user.id", default=None
    )

    notes: Optional[str] = Field(default=None)