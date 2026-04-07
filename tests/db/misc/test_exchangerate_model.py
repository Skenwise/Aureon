# tests/db/misc/test_exchangerate_model.py
"""Integration tests for ExchangeRate model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

from database.model.misc.currency import Currency
from database.model.misc.exchange_rate import ExchangeRate


def test_create_exchange_rate(db_session):
    """Create a valid ExchangeRate record and verify it persists correctly."""
    # Create dependencies
    currency_usd = Currency(code="USD", name="US Dollar", decimals=2)
    currency_zmw = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    
    db_session.add_all([currency_usd, currency_zmw])
    db_session.commit()

    exchange_rate = ExchangeRate(
        base_currency="USD",
        quote_currency="ZMW",
        rate=25.50,
        valid_from=datetime.now(timezone.utc)
    )
    db_session.add(exchange_rate)
    db_session.commit()

    retrieved = db_session.get(ExchangeRate, exchange_rate.id)
    assert retrieved is not None
    assert retrieved.base_currency == "USD"
    assert retrieved.quote_currency == "ZMW"
    assert retrieved.rate == 25.50


def test_exchange_rate_unique_constraints(db_session):
    """Duplicate exchange rate pair should raise IntegrityError."""
    currency_usd = Currency(code="EUR", name="Euro", decimals=2)
    currency_gbp = Currency(code="GBP", name="British Pound", decimals=2)
    
    db_session.add_all([currency_usd, currency_gbp])
    db_session.commit()

    rate1 = ExchangeRate(base_currency="EUR", quote_currency="GBP", rate=0.85)
    rate2 = ExchangeRate(base_currency="EUR", quote_currency="GBP", rate=0.86)

    db_session.add(rate1)
    db_session.commit()

    db_session.add(rate2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_exchange_rate_relationships(db_session):
    """Test ExchangeRate to Currency relationships."""
    currency_usd = Currency(code="CAD", name="Canadian Dollar", decimals=2)
    currency_eur = Currency(code="EUR", name="Euro", decimals=2)
    
    db_session.add_all([currency_usd, currency_eur])
    db_session.commit()

    exchange_rate = ExchangeRate(
        base_currency="CAD",
        quote_currency="EUR",
        rate=0.68
    )
    db_session.add(exchange_rate)
    db_session.commit()

    assert exchange_rate.base_currency == "CAD"
    assert exchange_rate.quote_currency == "EUR"