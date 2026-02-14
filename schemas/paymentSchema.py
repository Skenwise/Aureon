# schemas/paymentSchema.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# ==================== PAYMENT SCHEMAS ====================

class PaymentCreate(BaseModel):
    """
    Schema for creating a payment.
    Base schema for all payment types.
    """
    payment_type: Literal["INBOUND", "OUTBOUND", "SETTLEMENT"] = Field(..., description="Payment type")
    direction: Literal["IN", "OUT", "INTERNAL"] = Field(..., description="Payment direction")
    amount: Decimal = Field(..., gt=0, description="Payment amount (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    source_account_id: Optional[UUID] = Field(None, description="Source account ID")
    destination_account_id: Optional[UUID] = Field(None, description="Destination account ID")
    provider_type: Literal["INTERNAL", "MOBILE_MONEY", "BANK"] = Field(..., description="Payment provider type")
    provider_id: Optional[UUID] = Field(None, description="Payment provider ID")
    reference: Optional[str] = Field(None, max_length=100, description="User reference")
    notes: Optional[str] = Field(None, max_length=500, description="Payment notes")
    
    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        return v


class PaymentUpdate(BaseModel):
    """
    Schema for updating a payment.
    Typically only status updates are allowed.
    """
    status: Optional[Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED", "REVERSED"]] = Field(
        None, description="Updated payment status"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Updated notes")


class PaymentRead(BaseModel):
    """
    Schema for reading payment data.
    """
    id: UUID
    payment_number: str
    payment_type: str
    direction: str
    amount: Decimal
    currency: str
    status: str
    source_account_id: Optional[UUID]
    destination_account_id: Optional[UUID]
    provider_type: str
    provider_id: Optional[UUID]
    provider_reference: Optional[str]
    external_transaction_id: Optional[UUID]
    journal_entry_id: Optional[UUID]
    reference: Optional[str]
    notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== INBOUND PAYMENT SCHEMAS ====================

class InboundPaymentCreate(BaseModel):
    """
    Schema for creating an inbound payment (money entering system).
    """
    amount: Decimal = Field(..., gt=0, description="Payment amount (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    destination_account_id: UUID = Field(..., description="Destination account ID")
    provider_type: Literal["MOBILE_MONEY", "BANK", "INTERNAL"] = Field(..., description="Payment provider type")
    provider_id: Optional[UUID] = Field(None, description="Payment provider ID")
    provider_reference: Optional[str] = Field(None, max_length=150, description="External provider reference")
    external_transaction_id: Optional[UUID] = Field(None, description="Link to external transaction")
    reference: Optional[str] = Field(None, max_length=100, description="User reference")
    notes: Optional[str] = Field(None, max_length=500, description="Payment notes")
    
    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        return v


class InboundPaymentRead(BaseModel):
    """
    Schema for reading inbound payment data.
    """
    id: UUID
    payment_number: str
    amount: Decimal
    currency: str
    status: str
    destination_account_id: UUID
    provider_type: str
    provider_id: Optional[UUID]
    provider_reference: Optional[str]
    external_transaction_id: Optional[UUID]
    journal_entry_id: Optional[UUID]
    reference: Optional[str]
    notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== OUTBOUND PAYMENT SCHEMAS ====================

class OutboundPaymentCreate(BaseModel):
    """
    Schema for creating an outbound payment (money leaving system).
    """
    amount: Decimal = Field(..., gt=0, description="Payment amount (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    source_account_id: UUID = Field(..., description="Source account ID")
    destination_account_id: Optional[UUID] = Field(None, description="Destination account ID (if internal)")
    provider_type: Literal["INTERNAL", "MOBILE_MONEY", "BANK"] = Field(..., description="Payment provider type")
    provider_id: Optional[UUID] = Field(None, description="Payment provider ID")
    destination_details: Optional[dict] = Field(None, description="External destination details (phone, account number, etc.)")
    reference: Optional[str] = Field(None, max_length=100, description="User reference")
    notes: Optional[str] = Field(None, max_length=500, description="Payment notes")
    
    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        return v


class OutboundPaymentRead(BaseModel):
    """
    Schema for reading outbound payment data.
    """
    id: UUID
    payment_number: str
    amount: Decimal
    currency: str
    status: str
    source_account_id: UUID
    destination_account_id: Optional[UUID]
    provider_type: str
    provider_id: Optional[UUID]
    provider_reference: Optional[str]
    journal_entry_id: Optional[UUID]
    reference: Optional[str]
    notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== SETTLEMENT SCHEMAS ====================

class SettlementCreate(BaseModel):
    """
    Schema for creating an internal settlement.
    """
    amount: Decimal = Field(..., gt=0, description="Settlement amount (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    source_account_id: UUID = Field(..., description="Source account ID")
    destination_account_id: UUID = Field(..., description="Destination account ID")
    settlement_type: str = Field(..., max_length=50, description="Settlement type (LOAN_REPAYMENT, INTERNAL_TRANSFER, etc.)")
    reference: Optional[str] = Field(None, max_length=100, description="User reference")
    notes: Optional[str] = Field(None, max_length=500, description="Settlement notes")
    
    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Settlement amount must be positive")
        return v


class SettlementRead(BaseModel):
    """
    Schema for reading settlement data.
    """
    id: UUID
    payment_number: str
    amount: Decimal
    currency: str
    status: str
    source_account_id: UUID
    destination_account_id: UUID
    settlement_type: str
    journal_entry_id: Optional[UUID]
    reference: Optional[str]
    notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== PAYMENT EXECUTION SCHEMAS ====================

class PaymentExecutionRead(BaseModel):
    """
    Schema for reading payment execution attempt data.
    """
    id: UUID
    payment_id: UUID
    provider_id: Optional[UUID]
    attempt_number: int
    status: Literal["INITIATED", "SUCCESS", "FAILED"]
    provider_response: Optional[str]
    provider_transaction_id: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    executed_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== PROVIDER RESPONSE SCHEMAS ====================

class ProviderExecutionResult(BaseModel):
    """
    Schema for provider execution result.
    Returned by payment providers after execution attempt.
    """
    success: bool
    provider_transaction_id: Optional[str] = None
    provider_reference: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict] = None