"""
Reporting Module - Port/Adapter Layer.

Read-only projections for dashboards and analytics.
Each adapter injects the corresponding ReportingProvider.
"""

from .ledger_views import LedgerReportPort, LedgerReportAdapter
from .loan_reports import LoanReportPort, LoanReportAdapter
from .payment_reports import PaymentReportPort, PaymentReportAdapter
from .compliance import ComplianceReportPort, ComplianceReportAdapter
from .errors import ReportingError, ReportGenerationError

__all__ = [
    "LedgerReportPort",
    "LedgerReportAdapter",
    "LoanReportPort",
    "LoanReportAdapter",
    "PaymentReportPort",
    "PaymentReportAdapter",
    "ComplianceReportPort",
    "ComplianceReportAdapter",
    "ReportingError",
    "ReportGenerationError",
]