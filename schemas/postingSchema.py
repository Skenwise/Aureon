# schemas/postingSchema.py
from pydantic import BaseModel, Field, condecimal
from typing import Optional, Annotated
from uuid import UUID
from decimal import Decimal
from datetime import datetime

# Define the type once at the top of your file
PositiveDecimal = Annotated[Decimal, Field(gt=0, decimal_places=2)]

class PostingCreate(BaseModel):
    """Schema for creating a new ledger posting."""

    debit_account_id: UUID = Field(
        ...,
        description="UUID of the account to debit.",
    )
    credit_account_id: UUID = Field(
        ...,
        description="UUID of the account to credit.",
    )
    amount: PositiveDecimal = Field(
        ...,
        description="Positive amount to transfer. Single-currency only.",
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO currency code (e.g., USD, ZMW).",
    )
    reference: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional reference for audit or tracking purposes.",
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Time the posting was created. Defaults to UTC now if not provided.",
    )


class PostingUpdate(BaseModel):
    """Schema for updating an existing posting.

    Only provided fields will be updated. Rarely used in practice.
    """

    reference: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated reference.",
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Updated posting timestamp.",
    )


class PostingRead(BaseModel):
    """Schema for returning posting data in read-only format."""

    id: UUID
    debit_account_id: UUID
    credit_account_id: UUID
    amount: PositiveDecimal
    currency: str
    reference: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM compatibility."""
        orm_mode = True
