# models/core/company.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional

from database.model.treasury.funding_transfer import FundingTransfer
from database.model.treasury.fund_reservation import FundReservation
from database.model.treasury.cash_position import CashPosition
from ..base import BaseModel

class Company(BaseModel, table=True):
    """
    Represents a tenant company in Aureon
    """
    code: str = Field(..., max_length=50, unique=True, index=True)
    name: str = Field(..., max_length=150)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    currency: Optional[str] = Field(default="USD", max_length=3)
    subscription_tier: Optional[str] = Field(default=None)
    subscription_status: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)

    cash_positions: list["CashPosition"] = Relationship(back_populates="company")
    fund_reservations: list["FundReservation"] = Relationship(back_populates="company")
    funding_transfers: list["FundingTransfer"] = Relationship(back_populates="company")