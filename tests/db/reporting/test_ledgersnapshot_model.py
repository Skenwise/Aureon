# tests/db/reporting/test_ledgersnapshot_model.py
"""Integration tests for LedgerSnapshot model using isolated database harness."""

from datetime import date, datetime, timezone
from decimal import Decimal

from database.model.core.company import Company
from database.model.finance.account import Account
from database.model.misc.currency import Currency
from database.model.reporting.ledger_snapshot import LedgerSnapshot


def test_create_ledger_snapshot(db_session):
    """Create a valid LedgerSnapshot record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="LEDGCO", name="Ledger Company")
    account = Account(account_number="1000", account_type="ASSET", currency="USD")
    
    db_session.add_all([currency, company, account])
    db_session.commit()

    snapshot = LedgerSnapshot(
        tenant_id=company.id,
        snapshot_date=date.today(),
        account_id=account.id,
        account_code="1000",
        account_name="Cash",
        account_type="ASSET",
        balance=Decimal("10000.00"),
        debit_count=5,
        credit_count=3
    )
    db_session.add(snapshot)
    db_session.commit()

    retrieved = db_session.get(LedgerSnapshot, snapshot.id)
    assert retrieved is not None
    assert retrieved.account_code == "1000"
    assert retrieved.balance == Decimal("10000.00")
    assert retrieved.debit_count == 5