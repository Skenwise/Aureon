#model/reporting/ledger_snapshot.py

"""
Ledger Snapshot Model.

Materialized daily snapshot of account balances.
Used for fast balance sheet and income statement queries.
"""

from sqlmodel import SQLModel, Field, Index
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from database.model.base import BaseModel


class LedgerSnapshot(BaseModel, table=True):
    """
    Daily snapshot of account balances.
    Refreshed daily after end-of-day processing.
    """
    __table_args__ = (
        Index("idx_ledger_snapshot_tenant_date", "tenant_id", "snapshot_date"),
        Index("idx_ledger_snapshot_account", "account_id"),
    )
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="company.id", nullable=False)
    snapshot_date: date = Field(nullable=False)
    
    account_id: UUID = Field(foreign_key="account.id", nullable=False)
    account_code: str = Field(max_length=20)
    account_name: str = Field(max_length=100)
    account_type: str = Field(max_length=50)
    
    balance: Decimal = Field(default=Decimal("0"), max_digits=20, decimal_places=4)
    
    debit_count: int = Field(default=0)
    credit_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)