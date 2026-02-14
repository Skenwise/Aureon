# database/model/payments/payment_execution.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from ..base import BaseModel

if TYPE_CHECKING:
    from .payment import Payment
    from .payment_provder import PaymentProvider


class PaymentExecution(BaseModel, table=True):
    """
    Tracks each execution attempt for a payment.
    Multiple attempts may exist for a single payment (retries).
    """
    payment_id: UUID = Field(foreign_key="payment.id", index=True)
    provider_id: Optional[UUID] = Field(foreign_key="paymentprovider.id", default=None)
    
    attempt_number: int = Field(default=1, description="Execution attempt number")
    status: str = Field(default="INITIATED", max_length=20)
    # INITIATED, SUCCESS, FAILED
    
    # Provider response
    provider_response: Optional[str] = Field(default=None, description="Raw provider response")
    provider_transaction_id: Optional[str] = Field(default=None, max_length=150)
    error_code: Optional[str] = Field(default=None, max_length=50)
    error_message: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    payment: "Payment" = Relationship(back_populates="executions")
    payment_provider: Optional["PaymentProvider"] = Relationship()