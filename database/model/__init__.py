# database/model/__init__.py
from sqlmodel import SQLModel

# LEVEL 0: No dependencies (independent tables)
from database.model.base import BaseModel
from database.model.misc.currency import Currency
from database.model.misc.exchange_rate import ExchangeRate
from database.model.security.permission import SecurityPermission
from database.model.core.company import Company

# LEVEL 1: Depends only on Level 0
from database.model.core.customer import Customer
from database.model.security.role import SecurityRole, RolePermissionLink

# LEVEL 2: Depends on Level 0 & 1
from database.model.core.user import User
from database.model.finance.account import Account

# LEVEL 3: Depends on Level 2
from database.model.finance.journal import Journal
from database.model.finance.posting import Posting
from database.model.finance.loan import Loan
from database.model.payments.payment import Payment
from database.model.treasury.cash_position import CashPosition
from database.model.treasury.fund_reservation import FundReservation
from database.model.treasury.funding_transfer import FundingTransfer

# LEVEL 4: Depends on Level 3
from database.model.finance.loan_disbursement import LoanDisbursement
from database.model.finance.loan_repayment import LoanRepayment
from database.model.finance.loan_schedule import LoanSchedule
from database.model.payments.payment_execution import PaymentExecution
from database.model.payments.payment_provder import PaymentProvider
from database.model.payments.subscription import Subscription
from database.model.payments.transactions_external import ExternalTransaction
from database.model.audit.audit_log import AuditLog
from database.model.audit.reconciliation import Reconciliation
from database.model.reporting.ledger_snapshot import LedgerSnapshot
from database.model.reporting.loan_portofolio import LoanPortfolioSnapshot
from database.model.reporting.payment_volume import PaymentVolumeSnapshot

# LEVEL 5: Additional finance models
from database.model.finance.fees import Fee
from database.model.finance.chart_of_account import ChartAccount

# All models list for reference
all_models = [
    "BaseModel",
    "Currency",
    "ExchangeRate",
    "SecurityPermission",
    "Company",
    "Customer",
    "SecurityRole",
    "RolePermissionLink",
    "User",
    "Account",
    "Journal",
    "Posting",
    "Loan",
    "Payment",
    "CashPosition",
    "FundReservation",
    "FundingTransfer",
    "LoanDisbursement",
    "LoanRepayment",
    "LoanSchedule",
    "PaymentExecution",
    "PaymentProvider",
    "Subscription",
    "ExternalTransaction",
    "AuditLog",
    "Reconciliation",
    "LedgerSnapshot",
    "LoanPortfolioSnapshot",
    "PaymentVolumeSnapshot",
    "Fee",
    "ChartOfAccount",
]

# SQLAlchemy metadata for migrations
metadata = SQLModel.metadata