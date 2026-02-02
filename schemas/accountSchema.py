# schemas/accountSchema.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class AccountCreate(BaseModel):
    """Schema for creating a new ledger account.

    This schema validates input data before it enters the
    accounting service or adapter layer.
    """

    code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Unique ledger account code (e.g. CASH_MAIN, LOAN_RECEIVABLE).",
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
    currency_code: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code the account is denominated in.",
    )
    parent_account_id: Optional[UUID] = Field(
        None,
        description="Optional parent account ID for chart-of-accounts hierarchy.",
    )


class AccountUpdate(BaseModel):
    """Schema for updating an existing ledger account.

    All fields are optional. Only provided fields will be updated.
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


class AccountRead(BaseModel):
    """Schema for returning ledger account data.

    Used by adapters and API layers to expose account information
    in a safe, read-only format.
    """

    id: UUID
    code: str
    name: str
    account_type: str
    currency_code: str
    parent_account_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True
