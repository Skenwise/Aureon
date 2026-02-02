from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ChartAccountCreate(BaseModel):
    """Schema for creating a new chart-of-accounts entry."""

    code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Unique account code (e.g., CASH_MAIN, LOAN_RECEIVABLE).",
    )
    name: str = Field(
        ...,
        max_length=100,
        description="Human-readable account name.",
    )
    account_type: str = Field(
        ...,
        description="Ledger account type: ASSET, LIABILITY, EQUITY, INCOME, or EXPENSE.",
    )
    parent_account_id: Optional[UUID] = Field(
        None,
        description="Optional parent account ID for hierarchical chart-of-accounts.",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional description of the account's purpose or usage.",
    )


class ChartAccountUpdate(BaseModel):
    """Schema for updating an existing chart-of-accounts entry.

    Only provided fields will be updated.
    """

    name: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated human-readable account name.",
    )
    parent_account_id: Optional[UUID] = Field(
        None,
        description="Updated parent account ID.",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated description.",
    )


class ChartAccountRead(BaseModel):
    """Schema for returning chart-of-accounts data in read-only format."""

    id: UUID
    code: str
    name: str
    account_type: str
    parent_account_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM compatibility."""
        orm_mode = True
