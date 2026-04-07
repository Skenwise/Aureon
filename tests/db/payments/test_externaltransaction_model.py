# tests/db/payments/test_externaltransaction_model.py
"""Integration tests for ExternalTransaction model using isolated database harness."""

import json
from datetime import datetime, timezone

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.payments.payment_provder import PaymentProvider
from database.model.payments.transactions_external import ExternalTransaction


def test_create_external_transaction(db_session):
    """Create a valid ExternalTransaction record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="EXTCO", name="External Company")
    provider = PaymentProvider(name="MTN", provider_type="mobile_money")
    
    db_session.add_all([currency, company, provider])
    db_session.commit()

    raw_payload = json.dumps({"transaction_id": "MTN123", "amount": 100})

    transaction = ExternalTransaction(
        provider_id=provider.id,
        provider_transaction_ref="MTN-TX-001",
        amount=100.00,
        currency="USD",
        status="confirmed",
        company_id=company.id,
        raw_payload=raw_payload
    )
    db_session.add(transaction)
    db_session.commit()

    retrieved = db_session.get(ExternalTransaction, transaction.id)
    assert retrieved is not None
    assert retrieved.provider_transaction_ref == "MTN-TX-001"
    assert retrieved.amount == 100.00
    assert retrieved.status == "confirmed"


def test_external_transaction_relationships(db_session):
    """Test ExternalTransaction to Company and PaymentProvider relationships."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELEXT", name="Relationship External Co")
    provider = PaymentProvider(name="AIRTEL", provider_type="mobile_money")
    
    db_session.add_all([currency, company, provider])
    db_session.commit()

    transaction = ExternalTransaction(
        provider_id=provider.id,
        provider_transaction_ref="AIRTEL-TX-001",
        amount=50,
        currency="ZMW",
        company_id=company.id
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.company is not None
    assert transaction.company.id == company.id
    assert transaction.payment_provider is not None
    assert transaction.payment_provider.id == provider.id