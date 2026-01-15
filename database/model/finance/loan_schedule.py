# models/finance/loan_schedule.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional
from ..base import BaseModel

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .loan import Loan
    
class LoanSchedule(BaseModel, table=True):
    """
    Represents a repayment schedule for a loan
    """
    loan_id: UUID = Field(foreign_key="loan.id", index=True)
    installment_number: int = Field(...)
    due_date: date = Field(...)
    principal_due: float = Field(...)
    interest_due: float = Field(...)
    total_due: float = Field(...)
    status: Optional[str] = Field(default="pending")  # pending, paid, overdue
    paid_date: Optional[date] = None
    metadata_: Optional[str] = Field(default=None)

    # Relationships
    loan: Optional["Loan"] = Relationship(back_populates="schedules")