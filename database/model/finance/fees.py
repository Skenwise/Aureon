# models/finance/fees.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional
from ..base import BaseModel
from ..finance.loan import Loan

class Fee(BaseModel, table=True):
    """
    Represents fees or penalties associated with a loan or account
    """
    loan_id: Optional[UUID] = Field(foreign_key="loan.id", default=None, index=True)
    name: str = Field(..., max_length=100)
    amount: float = Field(...)
    currency: str = Field(default="USD", max_length=3)
    due_date: Optional[date] = None
    status: Optional[str] = Field(default="pending")  # pending, paid, waived
    metadata_: Optional[str] = Field(default=None)

    # Relationships
    loan: Optional[Loan] = Relationship(back_populates="fees")