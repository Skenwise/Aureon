#backend/reporting/payment_reports.py

"""
Payment Reports Port & Adapter.

Provides read-only payment reports for transaction analytics and provider performance.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from datetime import date

from schemas.reportingSchema import (
    PaymentVolumeReport,
    PaymentMethodReport
)
from backend.reporting.errors import ReportGenerationError
from Middleware.DataProvider.ReportingProvider.payment_reports import PaymentReportsProvider


class PaymentReportPort(Protocol):
    """
    Port interface for payment reporting operations.
    """

    def get_payment_volume(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        currency: str = "USD"
    ) -> PaymentVolumeReport:
        """
        Get payment volume statistics over a date range.

        Args:
            company_id (UUID): Company/tenant identifier.
            start_date (date): Start of reporting period.
            end_date (date): End of reporting period.
            currency (str): Currency for volume reporting.

        Returns:
            PaymentVolumeReport: Volume statistics.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_payment_method_report(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> PaymentMethodReport:
        """
        Get payment distribution by method.

        Args:
            company_id (UUID): Company/tenant identifier.
            start_date (date): Start of reporting period.
            end_date (date): End of reporting period.

        Returns:
            PaymentMethodReport: Distribution by payment method.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError


class PaymentReportAdapter(PaymentReportPort):
    """
    Adapter implementation of PaymentReportPort.

    Delegates all reporting operations to PaymentReportsProvider
    and converts models to Pydantic schemas.
    """

    def __init__(self, provider: PaymentReportsProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (PaymentReportsProvider): Data provider for payment reports.
        """
        self.provider = provider

    def get_payment_volume(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        currency: str = "USD"
    ) -> PaymentVolumeReport:
        """
        Get payment volume via the provider.
        """
        try:
            return self.provider.get_payment_volume(company_id, start_date, end_date, currency)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate payment volume report: {str(e)}")

    def get_payment_method_report(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> PaymentMethodReport:
        """
        Get payment method report via the provider.
        """
        try:
            return self.provider.get_payment_method_report(company_id, start_date, end_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate payment method report: {str(e)}")