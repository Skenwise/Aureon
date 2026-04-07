# database/model/finance/account.py
from sqlmodel import Field, Relationship
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

from database.model.base import BaseModel

if TYPE_CHECKING:
    from .posting import Posting
    from .loan_disbursement import LoanDisbursement
    from database.model.core.company import Company
    from database.model.core.customer import Customer
    from database.model.treasury.cash_position import CashPosition


class Account(BaseModel, table=True):
    
    account_number: str = Field(..., unique=True, max_length=50)
    owner_customer_id: Optional[UUID] = Field(default=None, foreign_key="customer.id")
    account_type: str = Field(..., max_length=50)
    account_category: Optional[str] = Field(default=None, max_length=50)
    currency: str = Field(foreign_key="currency.code", max_length=3)
    balance: float = Field(default=0.0)
    locked_balance: float = Field(default=0.0)
    note: Optional[str] = Field(default=None)
    
    # Relationships
    owner_customer: Optional["Customer"] = Relationship(back_populates="accounts")
    company: Optional["Company"] = Relationship(back_populates="accounts")
    postings: List["Posting"] = Relationship(back_populates="account")
    loan_disbursements: List["LoanDisbursement"] = Relationship(back_populates="disbursement_account")
    cash_positions: List["CashPosition"] = Relationship(back_populates="linked_account")