# database/model/base.py
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


class BaseModel(SQLModel, table=False):
    """
    Base class for all tables.
    Abstract — does NOT create a table.
    Child classes must specify table=True.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    company_id: Optional[UUID] = Field(default=None, foreign_key="company.id", index=True)
    version: int = Field(default=1)


# Ensure BaseModel is exported
__all__ = ['BaseModel']