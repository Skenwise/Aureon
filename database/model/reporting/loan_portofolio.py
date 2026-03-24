# database/model/reporting/loan_portofolio.py

"""
Loan Portfolio Snapshot Model.

Materialized daily snapshot of loan portfolio status.
"""

from sqlmodel import SQLModel, Field, Index
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from database.model.base import BaseModel


class LoanPortfolioSnapshot(BaseModel, table=True):
    """
    Daily snapshot of loan portfolio.
    """
    __table_args__ = (
        Index("idx_loan_portfolio_tenant_date", "tenant_id", "snapshot_date"),
    )
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="company.id", nullable=False)
    snapshot_date: date = Field(nullable=False)
    
    loan_id: UUID = Field(foreign_key="loan.id", nullable=False)
    loan_number: str = Field(max_length=50)
    
    principal_amount: Decimal = Field(max_digits=20, decimal_places=4)
    outstanding_balance: Decimal = Field(max_digits=20, decimal_places=4)
    overdue_days: int = Field(default=0)
    
    status: str = Field(max_length=20)  # ACTIVE, CLOSED, DEFAULTED
    
    created_at: datetime = Field(default_factory=datetime.utcnow)