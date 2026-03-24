#Middleware/DataProvider/ReportingProvider/ledger_reports.py

"""
Compliance Reports Provider.

Provides read-only aggregation of audit data for compliance reporting.
Uses AuditProvider and ReconciliationProvider for source data.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
import json

from sqlmodel import Session

from Middleware.DataProvider.AuditProvider.audit_provider import AuditProvider
from Middleware.DataProvider.AuditProvider.reconciliation_provider import ReconciliationProvider
from schemas.auditSchema import AuditLogFilter, AuditAction, AuditSeverity
from schemas.reportingSchema import (
    AuditExportReport,
    ReconciliationReport,
    DailyActivitySummary
)


class ComplianceReportsProvider:
    """
    Provider for compliance-related reports.
    """

    def __init__(self, session: Session):
        self.session = session
        self.audit_provider = AuditProvider(session)
        self.reconciliation_provider = ReconciliationProvider(session)

    def get_audit_export(
        self,
        company_id: UUID,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10000
    ) -> AuditExportReport:
        """
        Export full audit trail for compliance.
        
        Senior Tip: Full audit export is required for regulatory audits.
        """
        # Create filter with all required parameters
        filter_params = AuditLogFilter(
            tenant_id=company_id,
            user_id=None,           # All users
            action=None,            # All actions
            severity=None,          # All severities
            entity_type=None,       # All entity types
            entity_id=None,         # All entities
            from_date=start_date,
            to_date=end_date,
            limit=limit,
            offset=0
        )
        
        logs = self.audit_provider.filter_logs(filter_params)
        
        entries = []
        for log in logs:
            # Parse changes JSON if present
            changes_data = None
            if log.changes:
                try:
                    changes_data = json.loads(log.changes)
                except:
                    changes_data = log.changes
            
            entries.append({
                "id": str(log.id),
                "performed_at": log.performed_at.isoformat() if log.performed_at else None,
                "performed_by": str(log.performed_by) if log.performed_by else None,
                "action": log.action,
                "entity": log.entity,
                "entity_id": str(log.entity_id) if log.entity_id else None,
                "changes": changes_data,
                "ip_address": log.ip_address
            })
        
        return AuditExportReport(
            tenant_id=company_id,
            start_date=start_date,
            end_date=end_date,
            total_entries=len(entries),
            entries=entries
        )

    def get_reconciliation_summary(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> ReconciliationReport:
        """
        Get reconciliation summary over a date range.
        
        Senior Tip: Reconciliation reports prove system accuracy to auditors.
        """
        reconciliations = self.reconciliation_provider.list_reconciliations_by_tenant(
            company_id, 
            balanced=None
        )
        
        total_reconciled = 0
        total_discrepancies = 0
        open_discrepancies = 0
        resolved_discrepancies = 0
        
        daily_summary = []
        
        for rec in reconciliations:
            # Filter by date range
            if rec.business_date < start_date or rec.business_date > end_date:
                continue
            
            if rec.balanced:
                total_reconciled += 1
            else:
                total_discrepancies += 1
                
                # Check if resolved (using notes as indicator, or add status field)
                if rec.notes and "resolved" in rec.notes.lower():
                    resolved_discrepancies += 1
                else:
                    open_discrepancies += 1
            
            daily_summary.append({
                "date": rec.business_date.isoformat(),
                "balanced": rec.balanced,
                "difference": 0.0  # Would need difference field in Reconciliation model
            })
        
        return ReconciliationReport(
            tenant_id=company_id,
            start_date=start_date,
            end_date=end_date,
            total_reconciled=total_reconciled,
            total_discrepancies=total_discrepancies,
            open_discrepancies=open_discrepancies,
            resolved_discrepancies=resolved_discrepancies,
            daily_summary=daily_summary
        )

    def get_daily_activity_summary(
        self,
        business_date: date,
        company_id: UUID
    ) -> DailyActivitySummary:
        """
        Get daily system activity summary.
        
        Senior Tip: Daily summary is used for operational monitoring.
        """
        start_dt = datetime.combine(business_date, datetime.min.time())
        end_dt = datetime.combine(business_date, datetime.max.time())
        
        filter_params = AuditLogFilter(
            tenant_id=company_id,
            user_id=None,
            action=None,
            severity=None,
            entity_type=None,
            entity_id=None,
            from_date=start_dt,
            to_date=end_dt,
            limit=10000,
            offset=0
        )
        
        logs = self.audit_provider.filter_logs(filter_params)
        
        # Count activities by action
        new_loans = sum(1 for log in logs if log.action == "LOAN_CREATE")
        new_payments = sum(1 for log in logs if log.action in ["PAYMENT_CREATE", "PAYMENT_EXECUTE"])
        journal_entries = sum(1 for log in logs if log.action == "JOURNAL_POST")
        user_logins = sum(1 for log in logs if log.action == "LOGIN")
        system_errors = sum(1 for log in logs if log.action == "SYSTEM_ERROR")
        
        # Calculate payment volume from changes JSON
        payment_volume = Decimal("0")
        for log in logs:
            if log.action == "PAYMENT_EXECUTE" and log.changes:
                try:
                    changes = json.loads(log.changes)
                    payment_volume += Decimal(str(changes.get("amount", 0)))
                except:
                    pass
        
        return DailyActivitySummary(
            business_date=business_date,
            tenant_id=company_id,
            new_loans=new_loans,
            new_payments=new_payments,
            payment_volume=payment_volume,
            journal_entries=journal_entries,
            user_logins=user_logins,
            system_errors=system_errors
        )