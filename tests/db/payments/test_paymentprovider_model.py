# tests/db/payments/test_paymentprovider_model.py
"""Integration tests for PaymentProvider model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.payments.payment_provder import PaymentProvider


def test_create_payment_provider(db_session):
    """Create a valid PaymentProvider record and verify it persists correctly."""
    provider = PaymentProvider(
        name="MTN Mobile Money",
        provider_type="mobile_money",
        is_active=True,
        endpoint_url="https://api.mtn.com/v1"
    )
    db_session.add(provider)
    db_session.commit()

    retrieved = db_session.get(PaymentProvider, provider.id)
    assert retrieved is not None
    assert retrieved.name == "MTN Mobile Money"
    assert retrieved.provider_type == "mobile_money"
    assert retrieved.is_active is True


def test_payment_provider_unique_constraints(db_session):
    """Duplicate name should raise IntegrityError."""
    provider1 = PaymentProvider(name="AIRTEL", provider_type="mobile_money")
    provider2 = PaymentProvider(name="AIRTEL", provider_type="mobile_money")

    db_session.add(provider1)
    db_session.commit()

    db_session.add(provider2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_payment_provider_soft_delete(db_session):
    """Test deactivating a provider."""
    provider = PaymentProvider(name="BANK XYZ", provider_type="bank_transfer", is_active=True)
    db_session.add(provider)
    db_session.commit()

    assert provider.is_active is True

    provider.is_active = False
    db_session.add(provider)
    db_session.commit()

    retrieved = db_session.get(PaymentProvider, provider.id)
    assert retrieved.is_active is False