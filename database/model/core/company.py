# database/model/core/company.py
from sqlmodel import Field, Relationship
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

from database.model.base import BaseModel

if TYPE_CHECKING:
    from database.model.payments.payment import Payment
    from database.model.treasury.cash_position import CashPosition
    from database.model.treasury.fund_reservation import FundReservation
    from database.model.treasury.funding_transfer import FundingTransfer
    from database.model.finance.loan import Loan
    from database.model.finance.account import Account
    from database.model.core.customer import Customer
    from database.model.core.user import User
    from database.model.finance.journal import Journal
    from database.model.payments.subscription import Subscription


class Company(BaseModel, table=True):
    
    code: str = Field(..., max_length=50, unique=True, index=True)
    name: str = Field(..., max_length=150)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    currency: Optional[str] = Field(default="USD", max_length=3)
    subscription_tier: Optional[str] = Field(default=None)
    subscription_status: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    
    # Relationships
    payments: List["Payment"] = Relationship(back_populates="company")
    cash_positions: List["CashPosition"] = Relationship(back_populates="company")
    fund_reservations: List["FundReservation"] = Relationship(back_populates="company")
    funding_transfers: List["FundingTransfer"] = Relationship(back_populates="company")
    loans: List["Loan"] = Relationship(back_populates="company")
    accounts: List["Account"] = Relationship(back_populates="company")
    customers: List["Customer"] = Relationship(back_populates="company")
    users: List["User"] = Relationship(back_populates="company")
    journals: List["Journal"] = Relationship(back_populates="company")
    subscriptions: List["Subscription"] = Relationship(back_populates="company")