# tests/db/treasury/test_fundreservation_model.py
"""Integration tests for FundReservation model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.treasury.cash_position import CashPosition
from database.model.treasury.fund_reservation import FundReservation


def test_create_fund_reservation(db_session):
    """Create a valid FundReservation record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="RESCO", name="Reservation Company")
    cash_position = CashPosition(
        provider="MTN",
        account_id="MTN-ACC-001",
        currency_code="USD",
        company_id=company.id
    )
    
    db_session.add_all([currency, company, cash_position])
    db_session.commit()

    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    reservation = FundReservation(
        reservation_id="RES-001",
        cash_position_id=cash_position.id,
        provider="MTN",
        account_id="MTN-ACC-001",
        amount=500.00,
        currency_code="USD",
        transaction_ref="TXN-001",
        status="ACTIVE",
        expires_at=expires_at,
        note="Test reservation",
        company_id=company.id
    )
    db_session.add(reservation)
    db_session.commit()

    retrieved = db_session.get(FundReservation, reservation.id)
    assert retrieved is not None
    assert retrieved.reservation_id == "RES-001"
    assert retrieved.amount == 500.00
    assert retrieved.status == "ACTIVE"


def test_fund_reservation_unique_constraints(db_session):
    """Duplicate reservation_id should raise IntegrityError."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="UNIQRES", name="Unique Reservation Co")
    cash_position = CashPosition(
        provider="AIRTEL",
        account_id="AIRTEL-ACC-001",
        currency_code="ZMW",
        company_id=company.id
    )
    
    db_session.add_all([currency, company, cash_position])
    db_session.commit()

    res1 = FundReservation(
        reservation_id="UNIQ001",
        cash_position_id=cash_position.id,
        provider="AIRTEL",
        account_id="AIRTEL-ACC-001",
        amount=100,
        currency_code="ZMW",
        transaction_ref="TXN-001"
    )
    res2 = FundReservation(
        reservation_id="UNIQ001",
        cash_position_id=cash_position.id,
        provider="AIRTEL",
        account_id="AIRTEL-ACC-001",
        amount=200,
        currency_code="ZMW",
        transaction_ref="TXN-002"
    )

    db_session.add(res1)
    db_session.commit()

    db_session.add(res2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_fund_reservation_relationships(db_session):
    """Test FundReservation to CashPosition relationship."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="RELRES", name="Relationship Reservation Co")
    cash_position = CashPosition(
        provider="BANK",
        account_id="BANK-ACC-001",
        currency_code="EUR",
        company_id=company.id
    )
    
    db_session.add_all([currency, company, cash_position])
    db_session.commit()

    reservation = FundReservation(
        reservation_id="REL-001",
        cash_position_id=cash_position.id,
        provider="BANK",
        account_id="BANK-ACC-001",
        amount=300,
        currency_code="EUR",
        transaction_ref="TXN-REL-001"
    )
    db_session.add(reservation)
    db_session.commit()

    assert reservation.cash_position is not None
    assert reservation.cash_position.id == cash_position.id