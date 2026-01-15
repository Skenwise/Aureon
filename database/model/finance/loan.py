# models/finance/loan.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from ..base import BaseModel
from ..core.customer import Customer
from ..core.company import Company

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .loan_schedule import LoanSchedule

class Loan(BaseModel, table=True):
    """
    Represents a loan issued to a customer
    """
    customer_id: UUID = Field(foreign_key="customer.id", index=True)
    loan_number: str = Field(..., unique=True, max_length=50)
    principal_amount: float = Field(...)
    interest_rate: float = Field(..., description="Annual interest rate (%)")
    start_date: date = Field(default_factory=date.today)
    end_date: date
    term_months: int = Field(...)
    status: Optional[str] = Field(default="pending")  # pending, active, closed, defaulted
    currency: str = Field(default="USD", max_length=3)
    metadata_: Optional[str] = Field(default=None)

    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="loans")
    company: Optional["Company"] = Relationship(back_populates="loans")
    schedules: List["LoanSchedule"] = Relationship(back_populates="loan")