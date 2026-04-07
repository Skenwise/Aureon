# schemas/provider/currency.py
"""
Provider layer schemas for Currency operations.

These schemas define the boundary between Adapter and Provider.
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class CurrencyProviderInput(BaseModel):
    """
    Input schema for CurrencyProvider.create().
    
    What the Adapter sends to the Provider to create a currency.
    """
    code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., max_length=50, description="Full currency name")
    decimals: int = Field(default=2, ge=0, le=4, description="Number of decimal places")
    company_id: Optional[UUID] = Field(None, description="Tenant isolation")


class CurrencyProviderOutput(BaseModel):
    """
    Output schema for CurrencyProvider operations.
    
    What the Provider returns to the Adapter after database operations.
    """
    id: UUID
    code: str
    name: str
    decimals: int
    created_at: datetime
    updated_at: datetime
    company_id: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class CurrencyProviderFilter(BaseModel):
    """
    Filter schema for CurrencyProvider.list() operations.
    """
    code: Optional[str] = Field(None, min_length=3, max_length=3)
    name_contains: Optional[str] = Field(None, max_length=50)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)