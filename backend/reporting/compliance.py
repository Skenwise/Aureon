#backend/reporting/compliance.py

"""
Compliance Reports Port & Adapter.

Provides read-only compliance reports for audit and regulatory requirements.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from datetime import date, datetime

from schemas.reportingSchema import (
    AuditExportReport,
    ReconciliationReport,
    DailyActivitySummary
)
from backend.reporting.errors import ReportGenerationError
from Middleware.DataProvider.ReportingProvider.compliance_reports import ComplianceReportsProvider


class ComplianceReportPort(Protocol):
    """
    Port interface for compliance reporting operations.

    These reports are used for regulatory submissions and internal audits.
    """

    def get_audit_export(
        self,
        company_id: UUID,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10000
    ) -> AuditExportReport:
        """
        Export full audit trail for compliance.

        Args:
            company_id (UUID): Company/tenant identifier.
            start_date (datetime): Start of audit period.
            end_date (datetime): End of audit period.
            limit (int): Maximum number of records.

        Returns:
            AuditExportReport: Complete audit trail.

        Raises:
            ReportGenerationError: If export generation fails.
        """
        raise NotImplementedError

    def get_reconciliation_summary(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> ReconciliationReport:
        """
        Get reconciliation summary over a date range.

        Args:
            company_id (UUID): Company/tenant identifier.
            start_date (date): Start of reporting period.
            end_date (date): End of reporting period.

        Returns:
            ReconciliationReport: Reconciliation statistics.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError

    def get_daily_activity_summary(
        self,
        business_date: date,
        company_id: UUID
    ) -> DailyActivitySummary:
        """
        Get daily system activity summary.

        Args:
            business_date (date): Date for activity summary.
            company_id (UUID): Company/tenant identifier.

        Returns:
            DailyActivitySummary: Daily activity metrics.

        Raises:
            ReportGenerationError: If report generation fails.
        """
        raise NotImplementedError


class ComplianceReportAdapter(ComplianceReportPort):
    """
    Adapter implementation of ComplianceReportPort.

    Delegates all reporting operations to ComplianceReportsProvider
    and converts models to Pydantic schemas.
    """

    def __init__(self, provider: ComplianceReportsProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (ComplianceReportsProvider): Data provider for compliance reports.
        """
        self.provider = provider

    def get_audit_export(
        self,
        company_id: UUID,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10000
    ) -> AuditExportReport:
        """
        Get audit export via the provider.
        """
        try:
            return self.provider.get_audit_export(company_id, start_date, end_date, limit)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate audit export: {str(e)}")

    def get_reconciliation_summary(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> ReconciliationReport:
        """
        Get reconciliation summary via the provider.
        """
        try:
            return self.provider.get_reconciliation_summary(company_id, start_date, end_date)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate reconciliation summary: {str(e)}")

    def get_daily_activity_summary(
        self,
        business_date: date,
        company_id: UUID
    ) -> DailyActivitySummary:
        """
        Get daily activity summary via the provider.
        """
        try:
            return self.provider.get_daily_activity_summary(business_date, company_id)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate daily activity summary: {str(e)}")