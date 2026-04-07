# tests/db/payments/test_payment_model.py
"""Integration tests for Payment model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.finance.account import Account
from database.model.payments.payment import Payment


def test_create_payment(db_session):
    """Create a valid Payment record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="PAYCO", name="Payment Company")
    source_account = Account(account_number="SRC001", account_type="ASSET", currency="USD")
    dest_account = Account(account_number="DST001", account_type="ASSET", currency="USD")
    
    db_session.add_all([currency, company, source_account, dest_account])
    db_session.commit()

    payment = Payment(
        payment_number="PAY-001",
        payment_type="OUTBOUND",
        direction="OUT",
        amount=500.00,
        currency="USD",
        status="PENDING",
        source_account_id=source_account.id,
        destination_account_id=dest_account.id,
        provider_type="INTERNAL",
        reference="REF-001",
        notes="Test payment"
    )
    db_session.add(payment)
    db_session.commit()

    retrieved = db_session.get(Payment, payment.id)
    assert retrieved is not None
    assert retrieved.payment_number == "PAY-001"
    assert retrieved.amount == 500.00
    assert retrieved.status == "PENDING"


def test_payment_unique_constraints(db_session):
    """Duplicate payment_number should raise IntegrityError."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="UNIQPAY", name="Unique Payment Co")
    db_session.add_all([currency, company])
    db_session.commit()

    payment1 = Payment(
        payment_number="UNIQ001",
        payment_type="OUTBOUND",
        direction="OUT",
        amount=100,
        currency="ZMW",
        provider_type="INTERNAL"
    )
    payment2 = Payment(
        payment_number="UNIQ001",
        payment_type="INBOUND",
        direction="IN",
        amount=200,
        currency="ZMW",
        provider_type="INTERNAL"
    )

    db_session.add(payment1)
    db_session.commit()

    db_session.add(payment2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_payment_relationships(db_session):
    """Test Payment to Company and Account relationships."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="RELPAY", name="Relationship Payment Co")
    source_account = Account(account_number="RELSRC", account_type="ASSET", currency="EUR")
    
    db_session.add_all([currency, company, source_account])
    db_session.commit()

    payment = Payment(
        payment_number="REL-001",
        payment_type="OUTBOUND",
        direction="OUT",
        amount=300,
        currency="EUR",
        source_account_id=source_account.id,
        provider_type="INTERNAL",
        company_id=company.id
    )
    db_session.add(payment)
    db_session.commit()

    assert payment.company is not None
    assert payment.company.id == company.id
    assert payment.source_account is not None
    assert payment.source_account.id == source_account.id