from sqlmodel import SQLModel, Field, UniqueConstraint
from datetime import datetime, timezone
from typing import Optional
from database.model.base import BaseModel
from .currency import Currency


class ExchangeRate(BaseModel, table=True):
    """
    Represents currency exchange rates between base and quote currencies
    """
    __table_args__ = (
        UniqueConstraint('base_currency', 'quote_currency', name='uq_exchange_rate_pair'),
        UniqueConstraint('base_currency', 'quote_currency', 'valid_from', name='uq_exchange_rate_date'),
    )
    
    base_currency: str = Field(foreign_key="currency.code", max_length=3, index=True)
    quote_currency: str = Field(foreign_key="currency.code", max_length=3, index=True)
    rate: float = Field(..., description="Conversion rate from base to quote currency")
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_to: Optional[datetime] = None