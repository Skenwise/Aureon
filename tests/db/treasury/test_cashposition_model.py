# tests/db/treasury/test_cashposition_model.py
"""Integration tests for CashPosition model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.finance.account import Account
from database.model.treasury.cash_position import CashPosition


def test_create_cash_position(db_session):
    """Create a valid CashPosition record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="CASHCO", name="Cash Position Company")
    account = Account(account_number="CASH001", account_type="ASSET", currency="USD")
    
    db_session.add_all([currency, company, account])
    db_session.commit()

    cash_position = CashPosition(
        provider="MTN",
        account_id="MTN-ACC-001",
        currency_code="USD",
        total_balance=1000.00,
        available_balance=800.00,
        reserved_balance=200.00,
        linked_account_id=account.id,
        note="Test cash position",
        company_id=company.id
    )
    db_session.add(cash_position)
    db_session.commit()

    retrieved = db_session.get(CashPosition, cash_position.id)
    assert retrieved is not None
    assert retrieved.provider == "MTN"
    assert retrieved.account_id == "MTN-ACC-001"
    assert retrieved.total_balance == 1000.00
    assert retrieved.available_balance == 800.00
    assert retrieved.reserved_balance == 200.00


def test_cash_position_relationships(db_session):
    """Test CashPosition to Company and Account relationships."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELCASH", name="Relationship Cash Co")
    account = Account(account_number="RELCASH001", account_type="ASSET", currency="ZMW")
    
    db_session.add_all([currency, company, account])
    db_session.commit()

    cash_position = CashPosition(
        provider="AIRTEL",
        account_id="AIRTEL-ACC-001",
        currency_code="ZMW",
        linked_account_id=account.id,
        company_id=company.id
    )
    db_session.add(cash_position)
    db_session.commit()

    assert cash_position.company is not None
    assert cash_position.company.id == company.id
    assert cash_position.linked_account is not None
    assert cash_position.linked_account.id == account.id