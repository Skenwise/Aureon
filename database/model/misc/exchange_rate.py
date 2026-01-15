# models/misc/exchange_rate.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from ..base import BaseModel
from .currency import Currency

class ExchangeRate(BaseModel, table=True):
    """
    Represents currency exchange rates between base and quote currencies
    """
    base_currency: str = Field(foreign_key="currency.code", max_length=3, index=True)
    quote_currency: str = Field(foreign_key="currency.code", max_length=3, index=True)
    rate: float = Field(..., description="Conversion rate from base to quote currency")
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_to: Optional[datetime] = None