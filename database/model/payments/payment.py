# database/model/payments/payment.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from ..base import BaseModel
from ..core.company import Company
from ..finance.account import Account

if TYPE_CHECKING:
    from .payment_execution import PaymentExecution
    from .payment_provder import PaymentProvider
    from ..finance.journal import Journal


class Payment(BaseModel, table=True):
    """
    Represents a payment (inbound, outbound, or settlement) in the system.
    Tracks the intent and final status of money movement.
    """
    payment_number: str = Field(..., unique=True, max_length=50, description="Unique payment identifier")
    payment_type: str = Field(..., max_length=20, description="INBOUND, OUTBOUND, SETTLEMENT")
    direction: str = Field(..., max_length=20, description="IN, OUT, INTERNAL")
    
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(foreign_key="currency.code", max_length=3)
    
    status: str = Field(default="PENDING", max_length=20)
    # PENDING, PROCESSING, COMPLETED, FAILED, REVERSED
    
    # Source and destination
    source_account_id: Optional[UUID] = Field(foreign_key="account.id", default=None)
    destination_account_id: Optional[UUID] = Field(foreign_key="account.id", default=None)
    
    # Provider information
    provider_type: str = Field(..., max_length=50, description="INTERNAL, MOBILE_MONEY, BANK")
    provider_id: Optional[UUID] = Field(foreign_key="paymentprovider.id", default=None)
    provider_reference: Optional[str] = Field(default=None, max_length=150, description="External provider reference")
    
    # Links to other entities
    external_transaction_id: Optional[UUID] = Field(
        foreign_key="externaltransaction.id", 
        default=None,
        description="Link to external transaction if applicable"
    )
    journal_entry_id: Optional[UUID] = Field(
        foreign_key="journal.id",
        default=None,
        description="Accounting journal entry for this payment"
    )
    
    # Metadata
    reference: Optional[str] = Field(default=None, max_length=100, description="User reference")
    notes: Optional[str] = Field(default=None, max_length=500)
    metadata_: Optional[str] = Field(default=None, description="Additional JSON metadata")
    
    # Timestamps
    processed_at: Optional[datetime] = Field(default=None, description="When payment was processed")
    
    # Relationships
    company: "Company" = Relationship(back_populates="payments")
    source_account: Optional["Account"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Payment.source_account_id]"}
    )
    destination_account: Optional["Account"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Payment.destination_account_id]"}
    )
    payment_provider: Optional["PaymentProvider"] = Relationship(back_populates="payments")
    journal_entry: Optional["Journal"] = Relationship(back_populates="payments")
    executions: list["PaymentExecution"] = Relationship(back_populates="payment")