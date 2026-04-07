# tests/db/treasury/test_fundingtransfer_model.py
"""Integration tests for FundingTransfer model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.treasury.funding_transfer import FundingTransfer


def test_create_funding_transfer(db_session):
    """Create a valid FundingTransfer record and verify it persists correctly."""
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="FUNDCO", name="Funding Company")
    
    db_session.add_all([currency, company])
    db_session.commit()

    transfer = FundingTransfer(
        transfer_id="TRF-001",
        from_provider="MTN",
        from_account_id="MTN-SRC-001",
        to_provider="BANK",
        to_account_id="BANK-DST-001",
        amount=1000.00,
        currency_code="USD",
        status="COMPLETED",
        reference="REF-001",
        notes="Test transfer",
        company_id=company.id
    )
    db_session.add(transfer)
    db_session.commit()

    retrieved = db_session.get(FundingTransfer, transfer.id)
    assert retrieved is not None
    assert retrieved.transfer_id == "TRF-001"
    assert retrieved.from_provider == "MTN"
    assert retrieved.to_provider == "BANK"
    assert retrieved.amount == 1000.00
    assert retrieved.status == "COMPLETED"


def test_funding_transfer_unique_constraints(db_session):
    """Duplicate transfer_id should raise IntegrityError."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="UNIQFUND", name="Unique Funding Co")
    
    db_session.add_all([currency, company])
    db_session.commit()

    transfer1 = FundingTransfer(
        transfer_id="UNIQ001",
        from_provider="MTN",
        from_account_id="SRC001",
        to_provider="AIRTEL",
        to_account_id="DST001",
        amount=100,
        currency_code="ZMW"
    )
    transfer2 = FundingTransfer(
        transfer_id="UNIQ001",
        from_provider="MTN",
        from_account_id="SRC002",
        to_provider="BANK",
        to_account_id="DST002",
        amount=200,
        currency_code="ZMW"
    )

    db_session.add(transfer1)
    db_session.commit()

    db_session.add(transfer2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_funding_transfer_relationships(db_session):
    """Test FundingTransfer to Company relationship."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="RELFUND", name="Relationship Funding Co")
    
    db_session.add_all([currency, company])
    db_session.commit()

    transfer = FundingTransfer(
        transfer_id="REL-001",
        from_provider="MTN",
        from_account_id="SRC001",
        to_provider="BANK",
        to_account_id="DST001",
        amount=500,
        currency_code="EUR",
        company_id=company.id
    )
    db_session.add(transfer)
    db_session.commit()

    assert transfer.company is not None
    assert transfer.company.id == company.id