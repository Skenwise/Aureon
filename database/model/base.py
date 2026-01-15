# models/base.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class BaseModel(SQLModel):
    """
    Base class for all tables
    Includes:
    - id: UUID primary key
    - created_at, updated_at timestamps
    - company_id for multi-tenancy (foreign key to company table)
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    company_id: Optional[UUID] = Field(default=None, foreign_key="company.id", index=True)
