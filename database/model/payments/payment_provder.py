# models/payments/payment_provider.py
from sqlmodel import Relationship, SQLModel, Field
from uuid import UUID
from typing import Optional

from database.model.payments.payment import Payment
from ..base import BaseModel

class PaymentProvider(BaseModel, table=True):
    """
    Represents an external payment provider (e.g., mobile money, credit card gateway)
    """
    name: str = Field(..., max_length=100, unique=True)
    provider_type: str = Field(..., max_length=50)  # "mobile_money", "card", "bank_transfer", etc.
    api_key: Optional[str] = Field(default=None)
    api_secret: Optional[str] = Field(default=None)
    endpoint_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    metadata_: Optional[str] = Field(default=None)  # JSON stored as string
    payments: list["Payment"] = Relationship(back_populates="payment_provider")