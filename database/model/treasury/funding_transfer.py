# database/model/treasury/funding_transfer.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional
from datetime import datetime
from ..base import BaseModel
from ..core.company import Company

# Type checking imports
from typing import TYPE_CHECKING


class FundingTransfer(BaseModel, table=True):
    """
    Represents a transfer of funds between provider accounts.
    Used for topping up floats or rebalancing liquidity.
    """
    
    transfer_id: str = Field(..., unique=True, max_length=100, description="Unique transfer identifier")
    
    # Source
    from_provider: str = Field(..., max_length=50, description="Source provider")
    from_account_id: str = Field(..., max_length=100, description="Source account identifier")
    
    # Destination
    to_provider: str = Field(..., max_length=50, description="Destination provider")
    to_account_id: str = Field(..., max_length=100, description="Destination account identifier")
    
    # Amount
    amount: float = Field(..., gt=0, description="Transfer amount")
    currency_code: str = Field(foreign_key="currency.code", max_length=3)
    
    # Status
    status: str = Field(default="PENDING", max_length=20, description="PENDING, COMPLETED, FAILED, CANCELLED")
    
    # References
    reference: Optional[str] = Field(default=None, max_length=100, description="External reference number")
    notes: Optional[str] = Field(default=None, max_length=255, description="Transfer notes")
    
    # Timing
    completed_at: Optional[datetime] = Field(default=None, description="Transfer completion timestamp")
    
    # Relationships
    company: "Company" = Relationship(back_populates="funding_transfers")