# models/finance/loan_disbursement.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional
from ..base import BaseModel

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .loan import Loan
    from .account import Account
    from .journal import Journal


class LoanDisbursement(BaseModel, table=True):
    """
    Represents a loan disbursement transaction.
    Records the outbound fund transfer when a loan is funded.
    """
    loan_id: UUID = Field(foreign_key="loan.id", index=True)
    disbursement_amount: float = Field(...)
    disbursement_account_id: UUID = Field(foreign_key="account.id")
    disbursement_date: date = Field(...)
    payment_provider: str = Field(..., max_length=50)  # MTN, AIRTEL, BANK
    status: str = Field(default="PENDING", max_length=20)  # PENDING, COMPLETED, FAILED, CANCELLED
    reference: Optional[str] = Field(default=None, max_length=100)
    payment_transaction_id: Optional[str] = Field(default=None, max_length=100)
    journal_entry_id: Optional[UUID] = Field(foreign_key="journal.id", default=None)
    notes: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    loan: Optional["Loan"] = Relationship(back_populates="disbursements")
    disbursement_account: Optional["Account"] = Relationship(back_populates="loan_disbursements")
    journal_entry: Optional["Journal"] = Relationship(back_populates="loan_disbursements")