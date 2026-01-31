# schemas/currencySchema.py
from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime


class CurrencyCreate(BaseModel):
    """
    Schema for creating a new currency.
    Validates input data before passing to the service or adapter layer.
    """
    code: Annotated[str, StringConstraints(min_length=3, max_length=3)] = Field(..., description="ISO 4217 currency code (e.g., USD, ZMW)")
    symbol: str = Field(..., max_length=5, description="Currency symbol (e.g., $, ZK)")
    decimals: int = Field(..., ge=0, le=4, description="Number of decimal places used in the currency")
    name: Optional[str] = Field(None, max_length=50, description="Full currency name (e.g., US Dollar)")


class CurrencyUpdate(BaseModel):
    """
    Schema for updating an existing currency.
    Only provided fields are updated.
    """
    symbol: Optional[str] = Field(None, max_length=5, description="Updated currency symbol")
    decimals: Optional[int] = Field(None, ge=0, le=4, description="Updated decimal precision")
    name: Optional[str] = Field(None, max_length=50, description="Updated currency full name")


class CurrencyRead(BaseModel):
    """
    Schema for returning currency data from the service or API layer.
    """
    code: str
    symbol: str
    decimals: int
    name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # allows compatibility with ORM models
