# models/finance/loan_repayment.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional
from ..base import BaseModel

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .loan import Loan
    from .journal import Journal


class LoanRepayment(BaseModel, table=True):
    """
    Represents a loan repayment transaction.
    Records inbound payments from borrowers.
    """
    loan_id: UUID = Field(foreign_key="loan.id", index=True)
    payment_amount: float = Field(...)
    principal_applied: float = Field(..., description="Amount applied to principal reduction")
    interest_applied: float = Field(..., description="Amount applied to interest payment")
    payment_date: date = Field(...)
    payment_method: str = Field(..., max_length=50)  # MOBILE_MONEY, BANK_TRANSFER, CASH
    payment_provider: Optional[str] = Field(default=None, max_length=50)  # MTN, AIRTEL, BANK
    status: str = Field(default="PENDING", max_length=20)  # PENDING, APPLIED, REVERSED
    reference: Optional[str] = Field(default=None, max_length=100)
    payment_transaction_id: Optional[str] = Field(default=None, max_length=100)
    journal_entry_id: Optional[UUID] = Field(foreign_key="journal.id", default=None)
    notes: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    loan: Optional["Loan"] = Relationship(back_populates="repayments")
    journal_entry: Optional["Journal"] = Relationship(back_populates="loan_repayments")