# tests/db/test_account_model.py
"""Integration tests for Account model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.account import Account


def test_create_account(db_session):
    """Create a valid Account record and verify it persists correctly."""
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="ACCTCO", name="Account Company")
    customer = Customer(first_name="John", last_name="Doe", company_id=company.id)
    
    db_session.add_all([currency, company, customer])
    db_session.commit()

    account = Account(
        account_number="1000-001",
        owner_customer_id=customer.id,
        account_type="ASSET",
        account_category="CURRENT",
        currency="USD",
        balance=1000.00,
        locked_balance=0.00,
        note="Test account"
    )
    db_session.add(account)
    db_session.commit()

    retrieved = db_session.get(Account, account.id)
    assert retrieved is not None
    assert retrieved.account_number == "1000-001"
    assert retrieved.account_type == "ASSET"
    assert retrieved.balance == 1000.00


def test_account_unique_constraints(db_session):
    """Duplicate account_number should raise IntegrityError."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="UNIQCO", name="Unique Company")
    db_session.add_all([currency, company])
    db_session.commit()

    account1 = Account(account_number="UNIQ001", account_type="ASSET", currency="EUR")
    account2 = Account(account_number="UNIQ001", account_type="LIABILITY", currency="EUR")

    db_session.add(account1)
    db_session.commit()

    db_session.add(account2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_account_relationships(db_session):
    """Test Account to Customer and Company relationships."""
    currency = Currency(code="GBP", name="British Pound", decimals=2)
    company = Company(code="RELACCT", name="Relationship Account Co")
    customer = Customer(first_name="Jane", last_name="Smith", company_id=company.id)
    
    db_session.add_all([currency, company, customer])
    db_session.commit()

    account = Account(
        account_number="2000-001",
        owner_customer_id=customer.id,
        account_type="ASSET",
        currency="GBP",
        company_id=company.id  # ← Added
    )
    db_session.add(account)
    db_session.commit()

    assert account.owner_customer is not None
    assert account.owner_customer.id == customer.id
    assert account.company is not None
    assert account.company.id == company.id