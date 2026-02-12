# database/model/treasury/cash_position.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional
from datetime import datetime
from ..base import BaseModel
from ..core.company import Company
from ..finance.account import Account

# Type checking imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .fund_reservation import FundReservation


class CashPosition(BaseModel, table=True):
    """
    Represents real-time cash position for a provider account.
    Tracks actual money available in external systems (MTN, Airtel, Banks, Wallets).
    """
    
    provider: str = Field(..., max_length=50, description="Provider identifier (MTN, AIRTEL, BANK_ABC)")
    account_id: str = Field(..., max_length=100, description="External account identifier at provider")
    currency_code: str = Field(foreign_key="currency.code", max_length=3)
    
    # Balances
    total_balance: float = Field(default=0.0, description="Total balance in provider account")
    available_balance: float = Field(default=0.0, description="Available balance (total - reserved)")
    reserved_balance: float = Field(default=0.0, description="Balance locked for pending transactions")
    
    # Sync tracking
    last_synced_at: Optional[datetime] = Field(default=None, description="Last time balance was fetched from provider")
    
    
    # Optional link to internal ledger account
    linked_account_id: Optional[UUID] = Field(foreign_key="account.id", default=None)
    
    note: Optional[str] = Field(default=None)
    
    # Relationships
    company: "Company" = Relationship(back_populates="cash_positions")
    linked_account: Optional["Account"] = Relationship(back_populates="cash_positions")
    reservations: list["FundReservation"] = Relationship(back_populates="cash_position")