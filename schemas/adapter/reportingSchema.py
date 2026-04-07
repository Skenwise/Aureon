#schemas/reportingSchema.py

"""
Reporting Schemas.

Read-only projections for dashboards and analytics.
All schemas are for query results only — no write operations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum


# ==================== LEDGER REPORTS ====================

class AccountBalanceReport(BaseModel):
    """Account balance at a point in time."""
    account_id: UUID
    account_code: str
    account_name: str
    account_type: str
    currency: str
    balance: Decimal = Field(..., description="Current balance")
    debit_count: int = Field(..., description="Number of debit transactions")
    credit_count: int = Field(..., description="Number of credit transactions")
    last_activity: Optional[datetime] = None


class TrialBalanceReport(BaseModel):
    """Trial balance for a given date."""
    as_of_date: date
    tenant_id: UUID
    accounts: List[AccountBalanceReport]
    
    @property
    def total_debits(self) -> Decimal:
        total = Decimal("0")
        for a in self.accounts:
            if self._is_debit(a):
                total += a.balance
        return total
    
    @property
    def total_credits(self) -> Decimal:
        total = Decimal("0")
        for a in self.accounts:
            if not self._is_debit(a):
                total += a.balance
        return total
    
    @property
    def is_balanced(self) -> bool:
        return self.total_debits == self.total_credits
    
    def _is_debit(self, account: AccountBalanceReport) -> bool:
        asset_types = ["ASSET", "EXPENSE"]
        return account.account_type in asset_types


class BalanceSheetReport(BaseModel):
    """Balance sheet (Assets = Liabilities + Equity)."""
    as_of_date: date
    tenant_id: UUID
    
    assets: List[AccountBalanceReport]
    liabilities: List[AccountBalanceReport]
    equity: List[AccountBalanceReport]
    
    @property
    def total_assets(self) -> Decimal:
        total = Decimal("0")
        for a in self.assets:
            total += a.balance
        return total
    
    @property
    def total_liabilities(self) -> Decimal:
        total = Decimal("0")
        for a in self.liabilities:
            total += a.balance
        return total
    
    @property
    def total_equity(self) -> Decimal:
        total = Decimal("0")
        for a in self.equity:
            total += a.balance
        return total
    
    @property
    def is_balanced(self) -> bool:
        return self.total_assets == (self.total_liabilities + self.total_equity)


class IncomeStatementReport(BaseModel):
    """Income statement (Revenue - Expenses = Net Income)."""
    start_date: date
    end_date: date
    tenant_id: UUID
    
    revenue: List[AccountBalanceReport]
    expenses: List[AccountBalanceReport]
    
    @property
    def total_revenue(self) -> Decimal:
        total = Decimal("0")
        for a in self.revenue:
            total += a.balance
        return total
    
    @property
    def total_expenses(self) -> Decimal:
        total = Decimal("0")
        for a in self.expenses:
            total += a.balance
        return total
    
    @property
    def net_income(self) -> Decimal:
        return self.total_revenue - self.total_expenses


# ==================== LOAN REPORTS ====================

class LoanPortfolioSummary(BaseModel):
    """Summary of loan portfolio."""
    tenant_id: UUID
    as_of_date: date
    
    total_loans: int
    total_principal: Decimal
    total_interest_expected: Decimal
    total_outstanding: Decimal
    total_overdue: Decimal
    total_paid: Decimal
    
    portfolio_at_risk: float = Field(..., description="Percentage of loans overdue >30 days")
    average_loan_size: Decimal
    repayment_rate: float = Field(..., description="Percentage of expected payments received")
    
    @field_validator('portfolio_at_risk', 'repayment_rate', mode='before')
    @classmethod
    def validate_percentages(cls, v):
        if v is None:
            return 0.0
        return v


class LoanAgingReport(BaseModel):
    """Loans grouped by days overdue."""
    tenant_id: UUID
    as_of_date: date
    
    current: List[dict] = Field(default_factory=list)
    overdue_30_60: List[dict] = Field(default_factory=list)
    overdue_60_90: List[dict] = Field(default_factory=list)
    overdue_90_plus: List[dict] = Field(default_factory=list)
    
    @property
    def total_outstanding(self) -> Decimal:
        total = Decimal("0")
        for category in [self.current, self.overdue_30_60, self.overdue_60_90, self.overdue_90_plus]:
            for loan in category:
                total += loan.get("outstanding_balance", Decimal("0"))
        return total


class LoanRepaymentScheduleReport(BaseModel):
    """Upcoming repayments."""
    loan_id: UUID
    loan_number: str
    borrower_name: str
    installments: List[dict] = Field(default_factory=list)


# ==================== PAYMENT REPORTS ====================

class PaymentVolumeReport(BaseModel):
    """Payment volume over time period."""
    tenant_id: UUID
    start_date: date
    end_date: date
    currency: str
    
    total_transactions: int
    total_volume: Decimal
    successful_transactions: int
    failed_transactions: int
    success_rate: float
    daily_breakdown: List[dict] = Field(default_factory=list)
    
    @field_validator('success_rate', mode='before')
    @classmethod
    def validate_success_rate(cls, v):
        if v is None:
            return 0.0
        return v


class PaymentMethodReport(BaseModel):
    """Payment distribution by method."""
    tenant_id: UUID
    start_date: date
    end_date: date
    
    by_method: List[dict] = Field(default_factory=list)


class ProviderPerformanceReport(BaseModel):
    """Payment provider performance."""
    tenant_id: UUID
    start_date: date
    end_date: date
    
    provider_name: str
    total_attempts: int
    successful: int
    failed: int
    success_rate: float
    average_response_time_ms: float
    last_error: Optional[str]
    
    @field_validator('success_rate', mode='before')
    @classmethod
    def validate_success_rate(cls, v):
        if v is None:
            return 0.0
        return v


# ==================== COMPLIANCE REPORTS ====================

class AuditExportReport(BaseModel):
    """Full audit trail for compliance."""
    tenant_id: UUID
    start_date: datetime
    end_date: datetime
    total_entries: int
    entries: List[dict] = Field(default_factory=list)


class ReconciliationReport(BaseModel):
    """Reconciliation summary."""
    tenant_id: UUID
    start_date: date
    end_date: date
    
    total_reconciled: int
    total_discrepancies: int
    open_discrepancies: int
    resolved_discrepancies: int
    
    daily_summary: List[dict] = Field(default_factory=list)


class DailyActivitySummary(BaseModel):
    """Daily system activity."""
    business_date: date
    tenant_id: UUID
    
    new_loans: int
    new_payments: int
    payment_volume: Decimal
    journal_entries: int
    user_logins: int
    system_errors: int