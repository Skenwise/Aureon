#Middleware/DataProvider/ReportingProvider/payment_reports.py

"""
Payment Reports Provider.

Provides read-only aggregation of payment data for reporting.
Uses OutboundPaymentProvider, InboundPaymentProvider, and SettlementProvider.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlmodel import Session

from Middleware.DataProvider.PaymentProvider.outboundProvider import OutboundPaymentProvider
from Middleware.DataProvider.PaymentProvider.inboundProvider import InboundPaymentProvider
from Middleware.DataProvider.PaymentProvider.settlementProvider import SettlementProvider
from schemas.reportingSchema import (
    PaymentVolumeReport,
    PaymentMethodReport,
    ProviderPerformanceReport
)


class PaymentReportsProvider:
    """
    Provider for payment-related reports.
    Aggregates data from outbound, inbound, and settlement providers.
    """

    def __init__(self, session: Session):
        self.session = session
        self.outbound_provider = OutboundPaymentProvider(session)
        self.inbound_provider = InboundPaymentProvider(session)
        self.settlement_provider = SettlementProvider(session)

    def _get_all_payments(self, company_id: UUID) -> List:
        """
        Get all payments from all three providers and filter by company.
        
        Senior Tip: This is a private helper to avoid code duplication.
        """
        outbound = self.outbound_provider.list_outbound_payments()
        inbound = self.inbound_provider.list_inbound_payments()
        settlements = self.settlement_provider.list_settlements()
        
        all_payments = outbound + inbound + settlements
        
        # Filter by company_id
        return [p for p in all_payments if p.company_id == company_id]

    def get_payment_volume(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        currency: str = "USD"
    ) -> PaymentVolumeReport:
        """
        Get payment volume statistics over a date range.
        """
        payments = self._get_all_payments(company_id)
        
        total_transactions = 0
        total_volume = Decimal("0")
        successful = 0
        failed = 0
        
        for payment in payments:
            # Filter by date range
            if payment.created_at:
                payment_date = payment.created_at.date()
                if payment_date < start_date or payment_date > end_date:
                    continue
            
            total_transactions += 1
            total_volume += Decimal(str(payment.amount))
            
            status = payment.status.upper() if payment.status else ""
            if status in ["COMPLETED", "SUCCESS"]:
                successful += 1
            elif status in ["FAILED", "REJECTED", "CANCELLED"]:
                failed += 1
        
        success_rate = (successful / total_transactions * 100) if total_transactions > 0 else 0.0
        
        return PaymentVolumeReport(
            tenant_id=company_id,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            total_transactions=total_transactions,
            total_volume=total_volume,
            successful_transactions=successful,
            failed_transactions=failed,
            success_rate=success_rate,
            daily_breakdown=[]
        )

    def get_payment_method_report(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> PaymentMethodReport:
        """
        Get payment distribution by method (provider_type).
        """
        payments = self._get_all_payments(company_id)
        
        method_stats = {}
        
        for payment in payments:
            # Filter by date range
            if payment.created_at:
                payment_date = payment.created_at.date()
                if payment_date < start_date or payment_date > end_date:
                    continue
            
            method = payment.provider_type or "UNKNOWN"
            
            if method not in method_stats:
                method_stats[method] = {
                    "method": method,
                    "count": 0,
                    "volume": Decimal("0"),
                    "success_count": 0
                }
            
            method_stats[method]["count"] += 1
            method_stats[method]["volume"] += Decimal(str(payment.amount))
            
            status = payment.status.upper() if payment.status else ""
            if status in ["COMPLETED", "SUCCESS"]:
                method_stats[method]["success_count"] += 1
        
        # Calculate success rates
        by_method = []
        for method, stats in method_stats.items():
            success_rate = (stats["success_count"] / stats["count"] * 100) if stats["count"] > 0 else 0.0
            by_method.append({
                "method": method,
                "count": stats["count"],
                "volume": float(stats["volume"]),
                "success_rate": success_rate
            })
        
        return PaymentMethodReport(
            tenant_id=company_id,
            start_date=start_date,
            end_date=end_date,
            by_method=by_method
        )