# models/finance/account.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional, List
from ..base import BaseModel
from ..core.customer import Customer
from ..core.company import Company

# only import for type checking to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .posting import Posting

class Account(BaseModel, table=True):
    """
    Represents a financial account in the system (ledger account)
    """
    account_number: str = Field(..., unique=True, max_length=50)
    owner_customer_id: Optional[UUID] = Field(foreign_key="customer.id", default=None)
    account_type: str = Field(..., max_length=50)
    account_category: Optional[str] = Field(default=None, max_length=50)
    currency: str = Field(foreign_key="currency.code", max_length=3)
    balance: float = Field(default=0.0)
    locked_balance: float = Field(default=0.0)
    version: int = Field(default=1)
    note: Optional[str] = Field(default=None)

    # Relationships
    owner_customer: Optional[Customer] = Relationship(back_populates="accounts")
    company: Optional["Company"] = Relationship(back_populates="accounts")
    postings: List["Posting"] = Relationship(back_populates="account")