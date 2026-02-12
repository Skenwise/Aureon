# schemas/treasurySchema.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class CashPositionRead(BaseModel):
    """
    Schema for reading a cash position snapshot.
    Represents the actual balance available in a specific provider account.
    """
    provider: str = Field(..., description="Provider identifier (e.g., 'MTN', 'AIRTEL', 'BANK_ABC')")
    account_id: str = Field(..., description="Account identifier within the provider")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    total_balance: Decimal = Field(..., description="Total balance in the account")
    available_balance: Decimal = Field(..., description="Balance available for use (total - reserved)")
    reserved_balance: Decimal = Field(..., description="Balance reserved for pending transactions")
    as_of: datetime = Field(..., description="Timestamp when this balance was captured")
    
    @field_validator('total_balance', 'available_balance', 'reserved_balance')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v
    
    class Config:
        orm_mode = True


class LiquidityRead(BaseModel):
    """
    Schema for reading liquidity status across all providers.
    Aggregates available vs reserved funds.
    """
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    total_available: Decimal = Field(..., description="Total funds available across all providers")
    total_reserved: Decimal = Field(..., description="Total funds reserved for pending transactions")
    total_balance: Decimal = Field(..., description="Total funds (available + reserved)")
    positions: list[CashPositionRead] = Field(..., description="Breakdown by provider")
    as_of: datetime = Field(..., description="Timestamp of this liquidity snapshot")
    
    @field_validator('total_available', 'total_reserved', 'total_balance')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Liquidity totals cannot be negative")
        return v
    
    class Config:
        orm_mode = True


class FundingTransferCreate(BaseModel):
    """
    Schema for creating a funding transfer between providers.
    Validates input before executing the transfer.
    """
    from_provider: str = Field(..., description="Source provider identifier")
    from_account_id: str = Field(..., description="Source account identifier")
    to_provider: str = Field(..., description="Destination provider identifier")
    to_account_id: str = Field(..., description="Destination account identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    reference: Optional[str] = Field(None, max_length=100, description="External reference number")
    notes: Optional[str] = Field(None, max_length=255, description="Transfer notes or description")


class FundingTransferRead(BaseModel):
    """
    Schema for reading a completed or pending funding transfer.
    """
    transfer_id: str = Field(..., description="Unique transfer identifier")
    from_provider: str
    from_account_id: str
    to_provider: str
    to_account_id: str
    amount: Decimal
    currency_code: str
    status: Literal["PENDING", "COMPLETED", "FAILED", "CANCELLED"] = Field(..., description="Transfer status")
    reference: Optional[str]
    notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime] = Field(None, description="When the transfer was completed")
    
    class Config:
        orm_mode = True


class ReserveFundsCreate(BaseModel):
    """
    Schema for reserving funds before a payment execution.
    Ensures liquidity is locked for a pending transaction.
    """
    provider: str = Field(..., description="Provider where funds should be reserved")
    account_id: str = Field(..., description="Account identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to reserve (must be positive)")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    transaction_ref: str = Field(..., description="Reference to the transaction requiring this reservation")
    expires_at: Optional[datetime] = Field(None, description="When this reservation expires if not confirmed")


class ReserveFundsRead(BaseModel):
    """
    Schema for reading an active fund reservation.
    """
    reservation_id: str = Field(..., description="Unique reservation identifier")
    provider: str
    account_id: str
    amount: Decimal
    currency_code: str
    transaction_ref: str
    status: Literal["ACTIVE", "RELEASED", "CONFIRMED"] = Field(..., description="Reservation status")
    created_at: datetime
    expires_at: Optional[datetime]
    released_at: Optional[datetime] = Field(None, description="When the reservation was released or confirmed")
    
    class Config:
        orm_mode = True


class ProviderBalanceRead(BaseModel):
    """
    Schema for raw balance data fetched from an external provider API.
    This is the adapter output before being normalized into CashPosition.
    """
    provider: str = Field(..., description="Provider identifier")
    account_id: str = Field(..., description="Account identifier")
    balance: Decimal = Field(..., description="Raw balance from provider API")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    fetched_at: datetime = Field(..., description="When this balance was fetched from the provider")
    raw_response: Optional[dict] = Field(None, description="Raw API response for debugging")
    
    class Config:
        orm_mode = True