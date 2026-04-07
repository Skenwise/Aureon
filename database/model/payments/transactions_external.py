# models/payments/transactions_external.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from database.model.base import BaseModel
from .payment_provder import PaymentProvider
from database.model.core.company import Company

if TYPE_CHECKING:
    from .payment import Payment

class ExternalTransaction(BaseModel, table=True):
    """
    Represents a transaction received from an external payment provider
    (mobile money, card, bank transfer)
    """
    provider_id: UUID = Field(foreign_key="paymentprovider.id", index=True)

    provider_transaction_ref: str = Field(..., max_length=150, index=True)
    amount: float = Field(...)
    currency: str = Field(..., max_length=3)

    status: str = Field(default="received")  
    # received, confirmed, failed, reversed

    # Timestamp - Fixed: timezone-aware UTC
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Optional[str] = Field(default=None)  # full JSON from provider

    # Relationships
    company: Optional[Company] = Relationship()
    payment_provider: Optional[PaymentProvider] = Relationship()
    payments: List["Payment"] = Relationship(back_populates="external_transaction")