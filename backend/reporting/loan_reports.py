#backend/reporting/loan_reports.py

"""
Loan Reports Port & Adapter.

Provides read-only loan reports for portfolio management and risk assessment.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from datetime import date

from schemas.reportingSchema import (
    LoanPortfolioSummary,
    LoanAgingReport
)
from backend.reporting.errors import ReportGenerationError
from Middleware.DataProvider.ReportingProvider.loan_reports import LoanReportsProvider


class LoanReportPort(Protocol):
    """
    Port interface for loan reporting operations.
    """

    def get_portfolio_summary(self, company_id: UUID, as_of_date: date) -> LoanPortfolioSummary:
        """
        Get loan portfolio summary statistics.

        Args:
            company_id (UUID): Company/tenant identifier.
            as_of_date (date): Date for portfolio snapshot.

        Returns:
            LoanPortfolioSummary: Portfolio metrics.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_aging_report(self, company_id: UUID, as_of_date: date) -> LoanAgingReport:
        """
        Get loan aging report (overdue categorization).

        Args:
            company_id (UUID): Company/tenant identifier.
            as_of_date (date): Date for aging calculation.

        Returns:
            LoanAgingReport: Loans grouped by overdue days.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError


class LoanReportAdapter(LoanReportPort):
    """
    Adapter implementation of LoanReportPort.

    Delegates all reporting operations to LoanReportsProvider
    and converts models to Pydantic schemas.
    """

    def __init__(self, provider: LoanReportsProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (LoanReportsProvider): Data provider for loan reports.
        """
        self.provider = provider

    def get_portfolio_summary(self, company_id: UUID, as_of_date: date) -> LoanPortfolioSummary:
        """
        Get portfolio summary via the provider.
        """
        try:
            return self.provider.get_portfolio_summary(company_id, as_of_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate portfolio summary: {str(e)}")

    def get_aging_report(self, company_id: UUID, as_of_date: date) -> LoanAgingReport:
        """
        Get aging report via the provider.
        """
        try:
            return self.provider.get_loan_aging_report(company_id, as_of_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate aging report: {str(e)}")