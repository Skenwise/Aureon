"""
Payment Reports Provider.

Provides read-only aggregation of payment data for reporting.
Uses OutboundPaymentProvider, InboundPaymentProvider, and SettlementProvider.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

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

    def __init__(self, session: AsyncSession):
        self.session = session
        self.outbound_provider = OutboundPaymentProvider(session)
        self.inbound_provider = InboundPaymentProvider(session)
        self.settlement_provider = SettlementProvider(session)

    async def _get_all_payments(self, company_id: UUID) -> List:
        """
        Get all payments from all three providers and filter by company.
        
        Senior Tip: This is a private helper to avoid code duplication.
        """
        outbound = await self.outbound_provider.list_outbound_payments()
        inbound = await self.inbound_provider.list_inbound_payments()
        settlements = await self.settlement_provider.list_settlements()
        
        all_payments = outbound + inbound + settlements
        
        # Filter by company_id
        return [p for p in all_payments if hasattr(p, 'company_id') and p.company_id == company_id]

    async def get_payment_volume(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        currency: str = "USD"
    ) -> PaymentVolumeReport:
        """
        Get payment volume statistics over a date range.
        """
        payments = await self._get_all_payments(company_id)
        
        total_transactions = 0
        total_volume = Decimal("0")
        successful = 0
        failed = 0
        
        for payment in payments:
            # Filter by date range
            if hasattr(payment, 'created_at') and payment.created_at:
                payment_date = payment.created_at.date()
                if payment_date < start_date or payment_date > end_date:
                    continue
            
            total_transactions += 1
            total_volume += Decimal(str(getattr(payment, 'amount', 0)))
            
            status = getattr(payment, 'status', '').upper()
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
            total_volume=float(total_volume),
            successful_transactions=successful,
            failed_transactions=failed,
            success_rate=success_rate,
            daily_breakdown=[]
        )

    async def get_payment_method_report(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> PaymentMethodReport:
        """
        Get payment distribution by method (provider_type).
        """
        payments = await self._get_all_payments(company_id)
        
        method_stats = {}
        
        for payment in payments:
            # Filter by date range
            if hasattr(payment, 'created_at') and payment.created_at:
                payment_date = payment.created_at.date()
                if payment_date < start_date or payment_date > end_date:
                    continue
            
            method = getattr(payment, 'provider_type', 'UNKNOWN')
            
            if method not in method_stats:
                method_stats[method] = {
                    "method": method,
                    "count": 0,
                    "volume": Decimal("0"),
                    "success_count": 0
                }
            
            method_stats[method]["count"] += 1
            method_stats[method]["volume"] += Decimal(str(getattr(payment, 'amount', 0)))
            
            status = getattr(payment, 'status', '').upper()
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

    async def get_provider_performance(
        self,
        company_id: UUID,
        provider_type: Optional[str] = None,
        start_date: date = None,
        end_date: date = None
    ) -> ProviderPerformanceReport:
        """
        Get performance metrics by payment provider.
        """
        payments = await self._get_all_payments(company_id)
        
        provider_stats = {}
        
        for payment in payments:
            # Apply filters
            if start_date and hasattr(payment, 'created_at') and payment.created_at:
                if payment.created_at.date() < start_date:
                    continue
            if end_date and hasattr(payment, 'created_at') and payment.created_at:
                if payment.created_at.date() > end_date:
                    continue
            if provider_type and getattr(payment, 'provider_type', '') != provider_type:
                continue
            
            provider = getattr(payment, 'provider_type', 'UNKNOWN')
            
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "provider": provider,
                    "total_volume": Decimal("0"),
                    "successful_volume": Decimal("0"),
                    "failed_volume": Decimal("0"),
                    "avg_processing_time": 0.0
                }
            
            amount = Decimal(str(getattr(payment, 'amount', 0)))
            provider_stats[provider]["total_volume"] += amount
            
            status = getattr(payment, 'status', '').upper()
            if status in ["COMPLETED", "SUCCESS"]:
                provider_stats[provider]["successful_volume"] += amount
            elif status in ["FAILED", "REJECTED"]:
                provider_stats[provider]["failed_volume"] += amount
        
        performance = []
        for provider, stats in provider_stats.items():
            success_rate = (float(stats["successful_volume"]) / float(stats["total_volume"]) * 100) if stats["total_volume"] > 0 else 0.0
            performance.append({
                "provider": provider,
                "total_volume": float(stats["total_volume"]),
                "success_rate": success_rate,
                "avg_processing_time": stats["avg_processing_time"]
            })
        
        return ProviderPerformanceReport(
            tenant_id=company_id,
            provider_type=provider_type,
            start_date=start_date,
            end_date=end_date,
            providers=performance
        )
