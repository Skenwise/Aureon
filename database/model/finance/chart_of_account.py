from sqlmodel import SQLModel, Field, Relationship
from ..base import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class ChartAccount(BaseModel, table=True):
    """
    Represents a chart-of-accounts entry (ledger account definition)
    """
    code: str = Field(..., unique=True, max_length=20)
    name: str = Field(..., max_length=100)
    account_type: str = Field(..., max_length=20)
    parent_account_id: Optional[UUID] = Field(default=None, foreign_key="chartaccount.id")
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)

    # Relationships
    children: List["ChartAccount"] = Relationship(back_populates="parent")
    parent: Optional["ChartAccount"] = Relationship(back_populates="children")
