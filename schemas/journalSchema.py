# accounting/schemas/journalSchema.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from schemas.postingSchema import PostingCreate


class JournalCreate(BaseModel):
    """Schema for creating a new journal entry."""

    reference: str = Field(
        ...,
        max_length=100,
        description="Unique reference or identifier for the journal entry.",
    )
    source: str = Field(
        ...,
        max_length=50,
        description="Source system or module generating this journal (e.g., LOAN_MODULE).",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional description of the journal entry.",
    )
    postings: List[PostingCreate] = Field(
        ...,
        description="List of ledger postings that make up this journal entry. Must be >=1.",
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Creation time of the journal entry. Defaults to UTC now.",
    )

    @field_validator("postings")
    def postings_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError("Journal entry must contain at least one posting")
        return v


class JournalRead(BaseModel):
    """Schema for returning journal entries in read-only format."""

    id: UUID
    reference: str
    source: str
    description: Optional[str]
    postings: List[PostingCreate]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic ORM compatibility."""
        orm_mode = True
