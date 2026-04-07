# database/model/finance/journal.py
from sqlmodel import Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from database.model.base import BaseModel

if TYPE_CHECKING:
    from .posting import Posting
    from .loan_disbursement import LoanDisbursement
    from .loan_repayment import LoanRepayment
    from database.model.payments.payment import Payment
    from database.model.core.company import Company
    from database.model.core.user import User


class Journal(BaseModel, table=True):
    
    reference: str = Field(..., unique=True, max_length=100)
    description: Optional[str] = Field(default=None)
    total_debit: float = Field(default=0.0)
    total_credit: float = Field(default=0.0)
    currency: str = Field(foreign_key="currency.code", max_length=3)
    created_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    status: Optional[str] = Field(default="pending")
    processed_at: Optional[datetime] = Field(default=None)
    metadata_: Optional[str] = Field(default=None)
    source: str = Field(..., max_length=50)
    
    # Relationships
    company: Optional["Company"] = Relationship(back_populates="journals")
    creator: Optional["User"] = Relationship(back_populates="journals_created")
    postings: List["Posting"] = Relationship(back_populates="journal")
    payments: List["Payment"] = Relationship(back_populates="journal_entry")
    loan_disbursements: List["LoanDisbursement"] = Relationship(back_populates="journal_entry")
    loan_repayments: List["LoanRepayment"] = Relationship(back_populates="journal_entry")