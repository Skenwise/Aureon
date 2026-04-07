# API/dependencies.py
"""
Dependency Injection Container.

Wires all backend adapters and providers together.
One container instance per request.
"""

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.sessionmaker import get_async_db_session as get_session
from backend.core.error import AuthenticationError

# ============================================================================
# PROVIDER IMPORTS (Database Layer)
# ============================================================================

# Identity Providers
from Middleware.DataProvider.IdentityProvider.userProvider import UserProvider
from Middleware.DataProvider.IdentityProvider.roleProvider import SecurityRoleProvider
from Middleware.DataProvider.IdentityProvider.permissionProvider import SecurityPermissionProvider

# Tenant Provider
from Middleware.DataProvider.TenantProvider import TenantProvider

# Accounting Providers
from Middleware.DataProvider.AccountProvider.accountProvider import AccountProvider
from Middleware.DataProvider.AccountProvider.journalProvider import JournalProvider

# Loan Provider
from Middleware.DataProvider.LoanProvider.loanProvider import LoanProvider

# Payment Providers
from Middleware.DataProvider.PaymentProvider.outboundProvider import OutboundPaymentProvider
from Middleware.DataProvider.PaymentProvider.inboundProvider import InboundPaymentProvider
from Middleware.DataProvider.PaymentProvider.settlementProvider import SettlementProvider

# Treasury Providers
from Middleware.DataProvider.treasuryProvider.LiquidityProvider import LiquidityProvider
from Middleware.DataProvider.treasuryProvider.cashPositionProvider import CashPositionProvider
from Middleware.DataProvider.treasuryProvider.FundingProvider import FundingProvider

# Audit Providers
from Middleware.DataProvider.AuditProvider.audit_provider import AuditProvider
from Middleware.DataProvider.AuditProvider.reconciliation_provider import ReconciliationProvider

# Currency Provider
from Middleware.DataProvider.currencyProvider import CurrencyProvider

# Reporting Providers
from Middleware.DataProvider.ReportingProvider.ledger_reports import LedgerReportsProvider
from Middleware.DataProvider.ReportingProvider.loan_reports import LoanReportsProvider
from Middleware.DataProvider.ReportingProvider.payment_reports import PaymentReportsProvider
from Middleware.DataProvider.ReportingProvider.compliance_reports import ComplianceReportsProvider

# ============================================================================
# BACKEND ADAPTER IMPORTS (Business Logic Layer)
# ============================================================================

# Identity Adapters
from backend.identity.auth import AuthenticationAdapter
from backend.identity.user import UserManagementAdapter
from backend.identity.role import RoleAdapter

# Accounting Adapters
from backend.accounting.journal import JournalAdapter
from backend.accounting.account import AccountAdapter

# Treasury Adapters
from backend.treasury.liquidity import LiquidityAdapter
from backend.treasury.funding import FundingAdapter
from backend.treasury.cash_position import CashPositionAdapter

# Payment Adapters
from backend.payments.outbound import OutboundPaymentAdapter
from backend.payments.inbound import InboundPaymentAdapter
from backend.payments.settlement import SettlementAdapter

# Loan Adapter
from backend.loans.loan import LoanAdapter

# Audit Adapters
from backend.audit.audit import AuditAdapter
from backend.audit.reconciliation import ReconciliationAdapter

# Currency Adapter
from backend.currency.currency import CurrencyAdapter

# Reporting Adapters
from backend.reporting.ledger_views import LedgerReportAdapter
from backend.reporting.loan_reports import LoanReportAdapter
from backend.reporting.payment_reports import PaymentReportAdapter
from backend.reporting.compliance import ComplianceReportAdapter


class Container:
    """
    Dependency injection container.
    One instance per request.
    """

    def __init__(
        self,
        session: AsyncSession,  # Changed from Session to AsyncSession
        current_user: dict | None = None,
        current_tenant: str | None = None
    ):
        self.session = session
        self.current_user = current_user
        self.current_tenant = current_tenant

        self._init_providers()
        self._init_adapters()

    def _init_providers(self):
        """Initialize all data providers with the database session."""

        # Identity providers
        self.user_provider = UserProvider(self.session)
        self.role_provider = SecurityRoleProvider(self.session)
        self.permission_provider = SecurityPermissionProvider(self.session)

        # Tenant provider
        self.tenant_provider = TenantProvider(self.session)

        # Accounting providers
        self.account_provider = AccountProvider(self.session)
        self.journal_provider = JournalProvider(self.session)

        # Loan provider
        self.loan_provider = LoanProvider(self.session)

        # Payment providers
        self.outbound_payment_provider = OutboundPaymentProvider(self.session)
        self.inbound_payment_provider = InboundPaymentProvider(self.session)
        self.settlement_provider = SettlementProvider(self.session)

        # Treasury providers
        self.liquidity_provider = LiquidityProvider(self.session)
        self.cash_position_provider = CashPositionProvider(self.session)
        self.funding_provider = FundingProvider(self.session)

        # Audit providers
        self.audit_provider = AuditProvider(self.session)
        self.reconciliation_provider = ReconciliationProvider(self.session)

        # Currency provider
        self.currency_provider = CurrencyProvider(self.session)

        # Reporting providers
        self.ledger_reports_provider = LedgerReportsProvider(self.session)
        self.loan_reports_provider = LoanReportsProvider(self.session)
        self.payment_reports_provider = PaymentReportsProvider(self.session)
        self.compliance_reports_provider = ComplianceReportsProvider(self.session)

    def _init_adapters(self):
        """Initialize all backend adapters."""

        # ========== IDENTITY ADAPTERS ==========
        self.auth = AuthenticationAdapter(provider=self.user_provider)
        self.user = UserManagementAdapter(provider=self.user_provider)
        self.role = RoleAdapter(provider=self.role_provider)

        # ========== ACCOUNTING ADAPTERS ==========
        self.accounting_account = AccountAdapter(provider=self.account_provider)
        self.accounting_journal = JournalAdapter(provider=self.journal_provider)

        # ========== TREASURY ADAPTERS ==========
        self.liquidity = LiquidityAdapter(provider=self.liquidity_provider)
        self.cash_position = CashPositionAdapter(provider=self.cash_position_provider)
        self.funding = FundingAdapter(provider=self.funding_provider)

        # ========== PAYMENT ADAPTERS ==========
        self.payments_outbound = OutboundPaymentAdapter(provider=self.outbound_payment_provider)
        self.payments_inbound = InboundPaymentAdapter(provider=self.inbound_payment_provider)
        self.payments_settlement = SettlementAdapter(provider=self.settlement_provider)

        # ========== LOAN ADAPTER ==========
        self.loans = LoanAdapter(provider=self.loan_provider)

        # ========== AUDIT ADAPTERS ==========
        self.audit = AuditAdapter(provider=self.audit_provider)
        self.reconciliation = ReconciliationAdapter(provider=self.reconciliation_provider)

        # ========== CURRENCY ADAPTER ==========
        self.currency = CurrencyAdapter(provider=self.currency_provider)

        # ========== REPORTING ADAPTERS ==========
        self.reporting_ledger = LedgerReportAdapter(provider=self.ledger_reports_provider)
        self.reporting_loan = LoanReportAdapter(provider=self.loan_reports_provider)
        self.reporting_payment = PaymentReportAdapter(provider=self.payment_reports_provider)
        self.reporting_compliance = ComplianceReportAdapter(provider=self.compliance_reports_provider)


# ============================================================================
# FASTAPI DEPENDENCY FUNCTIONS
# ============================================================================

async def get_container(
    request: Request,
    session: AsyncSession = Depends(get_session)  # Changed to AsyncSession
) -> Container:
    """Create and return a container for the current request."""
    current_user = getattr(request.state, "user", None)
    current_tenant = getattr(request.state, "tenant", None)

    return Container(
        session=session,
        current_user=current_user,
        current_tenant=current_tenant
    )


async def get_current_user(
    container: Container = Depends(get_container)
) -> dict:
    """Get current authenticated user."""
    if not container.current_user:
        raise AuthenticationError("Not authenticated")
    return container.current_user


async def get_current_tenant(
    container: Container = Depends(get_container)
) -> str:
    """Get current tenant ID."""
    if not container.current_tenant:
        raise AuthenticationError("No tenant context")
    return container.current_tenant