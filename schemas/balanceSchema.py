# schemas/balanceSchema.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class AccountBalanceRead(BaseModel):
    """Schema for returning the balance of a single account."""

    account_id: UUID
    account_name: str
    account_type: str
    currency: str
    balance: Decimal
    last_updated: Optional[datetime]

    class Config:
        """Pydantic configuration for ORM compatibility."""
        orm_mode = True


class PeriodBalanceRead(BaseModel):
    """Schema for returning account balances over a specific period."""

    account_id: UUID
    account_name: str
    account_type: str
    currency: str
    period_start: datetime
    period_end: datetime
    opening_balance: Decimal
    closing_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal

    class Config:
        """Pydantic configuration for ORM compatibility."""
        orm_mode = True


class TrialBalanceItem(BaseModel):
    """Schema for a single line item in a trial balance."""

    account_id: UUID
    account_name: str
    account_type: str
    currency: str
    debit: Decimal
    credit: Decimal

    class Config:
        orm_mode = True


class TrialBalanceRead(BaseModel):
    """Schema for returning a complete trial balance."""

    company_id: Optional[UUID]
    currency: str
    items: List[TrialBalanceItem]
    total_debit: Decimal
    total_credit: Decimal
    generated_at: datetime

    class Config:
        orm_mode = True
