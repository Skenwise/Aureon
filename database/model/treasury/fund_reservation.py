# database/model/treasury/fund_reservation.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional
from datetime import datetime
from ..base import BaseModel
from ..core.company import Company

# Type checking imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cash_position import CashPosition


class FundReservation(BaseModel, table=True):
    """
    Represents a temporary lock on funds for pending transactions.
    Prevents double-spending by reserving funds before payment execution.
    """
    
    reservation_id: str = Field(..., unique=True, max_length=100, description="Unique reservation identifier")
    
    # Cash position reference
    cash_position_id: UUID = Field(foreign_key="cashposition.id")
    
    provider: str = Field(..., max_length=50, description="Provider where funds are reserved")
    account_id: str = Field(..., max_length=100, description="Account identifier at provider")
    
    # Amount
    amount: float = Field(..., gt=0, description="Amount reserved")
    currency_code: str = Field(foreign_key="currency.code", max_length=3)
    
    # Transaction reference
    transaction_ref: str = Field(..., max_length=100, description="Reference to payment/loan transaction")
    
    # Status
    status: str = Field(default="ACTIVE", max_length=20, description="ACTIVE, RELEASED, CONFIRMED")
    
    # Expiration
    expires_at: Optional[datetime] = Field(default=None, description="Reservation expiration time")
    released_at: Optional[datetime] = Field(default=None, description="When reservation was released/confirmed")
    
    note: Optional[str] = Field(default=None)
    
    # Relationships
    company: "Company" = Relationship(back_populates="fund_reservations")
    cash_position: "CashPosition" = Relationship(back_populates="reservations")