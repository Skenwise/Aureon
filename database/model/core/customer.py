# models/core/customer.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from database.model.base import BaseModel
from .company import Company

if TYPE_CHECKING:
    from database.model.finance.account import Account
    from database.model.finance.loan import Loan

class Customer(BaseModel, table=True):
    """
    Represents a customer of a company (tenant)
    """
    external_customer_ref: Optional[str] = Field(default=None, max_length=100)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)
    kyc_status: Optional[str] = Field(default="pending", max_length=50)
    metadata_: Optional[str] = Field(default=None)  # JSON stored as string

    # Relationships
    company: Optional[Company] = Relationship(back_populates="customers")
    accounts: List["Account"] = Relationship(back_populates="owner_customer")
    loans: List["Loan"] = Relationship(back_populates="customer")