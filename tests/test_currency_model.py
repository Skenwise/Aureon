# tests/test_currency_model.py
"""Integration tests for Currency model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from database.model.misc.currency import Currency


def test_create_currency(db_session):
    """Create a valid Currency record and verify it persists correctly."""
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    db_session.add(currency)
    db_session.commit()

    retrieved = db_session.get(Currency, currency.id)
    assert retrieved is not None
    assert retrieved.code == "USD"
    assert retrieved.name == "US Dollar"
    assert retrieved.decimals == 2

    stmt = select(Currency).where(Currency.code == "USD")
    result = db_session.execute(stmt)
    fetched = result.scalar_one()
    assert fetched.id == currency.id


def test_currency_unique_constraints(db_session):
    """Duplicate currency code should raise IntegrityError."""
    currency1 = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    currency2 = Currency(code="ZMW", name="Duplicate", decimals=2)

    db_session.add(currency1)
    db_session.commit()

    db_session.add(currency2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()