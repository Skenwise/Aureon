#backend/reporting/ledger_views.py

"""
Ledger Reports Port & Adapter.

Provides read-only ledger reports for dashboards and financial statements.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from datetime import date

from schemas.reportingSchema import (
    TrialBalanceReport,
    BalanceSheetReport,
    IncomeStatementReport,
    AccountBalanceReport
)
from backend.reporting.errors import ReportGenerationError
from Middleware.DataProvider.ReportingProvider.ledger_reports import LedgerReportsProvider


class LedgerReportPort(Protocol):
    """
    Port interface for ledger reporting operations.

    All reports are read-only and based on current ledger state.
    No writes, no mutations.
    """

    def get_trial_balance(self, company_id: UUID, as_of_date: date) -> TrialBalanceReport:
        """
        Get trial balance as of a specific date.

        Args:
            company_id (UUID): Company/tenant identifier.
            as_of_date (date): Date to calculate balances.

        Returns:
            TrialBalanceReport: All accounts with their balances.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_balance_sheet(self, company_id: UUID, as_of_date: date) -> BalanceSheetReport:
        """
        Get balance sheet (Assets = Liabilities + Equity).

        Args:
            company_id (UUID): Company/tenant identifier.
            as_of_date (date): Date for the balance sheet.

        Returns:
            BalanceSheetReport: Assets, liabilities, and equity.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_income_statement(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> IncomeStatementReport:
        """
        Get income statement for a date range.

        Args:
            company_id (UUID): Company/tenant identifier.
            start_date (date): Start of reporting period.
            end_date (date): End of reporting period.

        Returns:
            IncomeStatementReport: Revenue, expenses, net income.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_account_balance(
        self,
        account_id: UUID,
        as_of_date: date
    ) -> AccountBalanceReport:
        """
        Get single account balance as of a specific date.

        Args:
            account_id (UUID): Account identifier.
            as_of_date (date): Date to calculate balance.

        Returns:
            AccountBalanceReport: Account balance details.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError


class LedgerReportAdapter(LedgerReportPort):
    """
    Adapter implementation of LedgerReportPort.

    Delegates all reporting operations to LedgerReportsProvider
    and converts models to Pydantic schemas.
    """

    def __init__(self, provider: LedgerReportsProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (LedgerReportsProvider): Data provider for ledger reports.
        """
        self.provider = provider

    def get_trial_balance(self, company_id: UUID, as_of_date: date) -> TrialBalanceReport:
        """
        Get trial balance via the provider.
        """
        try:
            return self.provider.get_trial_balance(company_id, as_of_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate trial balance: {str(e)}")

    def get_balance_sheet(self, company_id: UUID, as_of_date: date) -> BalanceSheetReport:
        """
        Get balance sheet via the provider.
        """
        try:
            return self.provider.get_balance_sheet(company_id, as_of_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate balance sheet: {str(e)}")

    def get_income_statement(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> IncomeStatementReport:
        """
        Get income statement via the provider.
        """
        try:
            return self.provider.get_income_statement(company_id, start_date, end_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate income statement: {str(e)}")

    def get_account_balance(
        self,
        account_id: UUID,
        as_of_date: date
    ) -> AccountBalanceReport:
        """
        Get account balance via the provider.
        """
        try:
            return self.provider.get_account_balance(account_id, as_of_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to get account balance: {str(e)}")