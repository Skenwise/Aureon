# database/model/payments/payment.py
from sqlmodel import Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from database.model.base import BaseModel

if TYPE_CHECKING:
    from .payment_execution import PaymentExecution
    from .payment_provder import PaymentProvider
    from .transactions_external import ExternalTransaction
    from database.model.finance.account import Account
    from database.model.finance.journal import Journal
    from database.model.core.company import Company


class Payment(BaseModel, table=True):
    
    payment_number: str = Field(..., unique=True, max_length=50)
    payment_type: str = Field(..., max_length=20)
    direction: str = Field(..., max_length=20)
    
    amount: float = Field(...)
    currency: str = Field(foreign_key="currency.code", max_length=3)
    
    status: str = Field(default="PENDING", max_length=20)
    
    source_account_id: Optional[UUID] = Field(default=None, foreign_key="account.id")
    destination_account_id: Optional[UUID] = Field(default=None, foreign_key="account.id")
    
    provider_type: str = Field(..., max_length=50)
    provider_id: Optional[UUID] = Field(default=None, foreign_key="paymentprovider.id")
    provider_reference: Optional[str] = Field(default=None, max_length=150)
    
    external_transaction_id: Optional[UUID] = Field(default=None, foreign_key="externaltransaction.id")
    journal_entry_id: Optional[UUID] = Field(default=None, foreign_key="journal.id")
    
    reference: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    metadata_: Optional[str] = Field(default=None)
    
    processed_at: Optional[datetime] = Field(default=None)
    
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
    external_transaction: Optional["ExternalTransaction"] = Relationship(back_populates="payments")
    executions: List["PaymentExecution"] = Relationship(back_populates="payment")