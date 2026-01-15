# models/payments/subscription.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import date
from typing import Optional
from ..base import BaseModel
from ..core.company import Company
from .payment_provder import PaymentProvider

class Subscription(BaseModel, table=True):
    """
    Represents a company's subscription to the Aureon platform
    """
    provider_id: Optional[UUID] = Field(foreign_key="paymentprovider.id", default=None)
    plan_name: str = Field(..., max_length=100)
    status: str = Field(default="active")  # active, paused, cancelled, expired
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    auto_renew: bool = Field(default=True)
    provider_subscription_ref: Optional[str] = Field(default=None)
    metadata_: Optional[str] = Field(default=None)

    # Relationships
    company: Optional[Company] = Relationship(back_populates="subscriptions")
    payment_provider: Optional[PaymentProvider] = Relationship()