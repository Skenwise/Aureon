#database/model/reporting/payment_volume.py

"""
Payment Volume Snapshot Model.

Daily aggregation of payment statistics.
"""

from sqlmodel import SQLModel, Field, Index
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from database.model.base import BaseModel


class PaymentVolumeSnapshot(BaseModel, table=True):
    """
    Daily payment volume statistics.
    """
    __table_args__ = (
        Index("idx_payment_volume_tenant_date", "tenant_id", "snapshot_date"),
        Index("idx_payment_volume_provider", "provider"),
    )
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="company.id", nullable=False)
    snapshot_date: date = Field(nullable=False)
    
    provider: str = Field(max_length=50, description="Payment provider (INTERNAL, MTN, AIRTEL)")
    
    total_transactions: int = Field(default=0)
    total_volume: Decimal = Field(default=Decimal("0"), max_digits=20, decimal_places=4)
    successful: int = Field(default=0)
    failed: int = Field(default=0)
    
    average_response_ms: float = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)