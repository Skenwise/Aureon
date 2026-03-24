"""
Reporting Data Providers.

Read-only aggregation providers for dashboards and analytics.
These providers combine data from multiple source providers.
"""

from .ledger_reports import LedgerReportsProvider
from .loan_reports import LoanReportsProvider
from .payment_reports import PaymentReportsProvider
from .compliance_reports import ComplianceReportsProvider

__all__ = [
    "LedgerReportsProvider",
    "LoanReportsProvider", 
    "PaymentReportsProvider",
    "ComplianceReportsProvider",
]