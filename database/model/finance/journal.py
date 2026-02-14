# models/finance/journal.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from database.model.finance.loan_repayment import LoanRepayment
from ..base import BaseModel
from ..core.company import Company
from ..core.user import User
from ..misc.currency import Currency

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .posting import Posting
    from .loan_disbursement import LoanDisbursement
    from .loan_repayment import LoanRepayment
    
class Journal(BaseModel, table=True):
    """
    Represents a ledger journal (double-entry transaction)
    """
    reference: str = Field(..., unique=True, max_length=100)
    description: Optional[str] = Field(default=None)
    total_debit: float = Field(default=0.0)
    total_credit: float = Field(default=0.0)
    currency: str = Field(foreign_key="currency.code", max_length=3)
    created_by: Optional[UUID] = Field(foreign_key="user.id")
    status: Optional[str] = Field(default="pending")
    processed_at: Optional[datetime] = None
    metadata_: Optional[str] = Field(default=None)  # JSON stored as string
    source: str = Field(..., max_length=50, description="Source system or module generating this journal (e.g., LOAN_MODULE).")

    # Relationships
    company: Optional["Company"] = Relationship(back_populates="journals")
    creator: Optional["User"] = Relationship(back_populates="journals_created")
    postings: List["Posting"] = Relationship(back_populates="journal")
    loan_disbursements: List["LoanDisbursement"] = Relationship(back_populates="journal_entry")
    loan_repayments: List["LoanRepayment"] = Relationship(back_populates="journal_entry")