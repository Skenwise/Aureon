# database/model/finance/loan.py
from sqlmodel import Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional, List, TYPE_CHECKING

from database.model.base import BaseModel

if TYPE_CHECKING:
    from .loan_schedule import LoanSchedule
    from .loan_disbursement import LoanDisbursement
    from .loan_repayment import LoanRepayment
    from database.model.core.customer import Customer
    from database.model.core.company import Company
    from database.model.finance.fees import Fee


class Loan(BaseModel, table=True):
    
    customer_id: UUID = Field(foreign_key="customer.id", index=True)
    loan_number: str = Field(..., unique=True, max_length=50)
    principal_amount: float = Field(...)
    interest_rate: float = Field(...)
    start_date: date = Field(default_factory=date.today)
    end_date: date
    term_months: int = Field(...)
    status: Optional[str] = Field(default="pending")
    currency: str = Field(default="USD", max_length=3)
    metadata_: Optional[str] = Field(default=None)
    
    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="loans")
    company: Optional["Company"] = Relationship(back_populates="loans")
    schedules: List["LoanSchedule"] = Relationship(back_populates="loan")
    disbursements: List["LoanDisbursement"] = Relationship(back_populates="loan")
    repayments: List["LoanRepayment"] = Relationship(back_populates="loan")
    fees: List["Fee"] = Relationship(back_populates="loan")