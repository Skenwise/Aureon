# tests/providers/test_currency_provider.py
import pytest
from sqlalchemy.exc import IntegrityError
from typing import Any
from Middleware.DataProvider.currencyProvider import CurrencyProvider
from schemas.provider.currency import CurrencyProviderFilter
from backend.core.error import NotFoundError, ValidationError, CalculationError


@pytest.mark.asyncio
async def test_get_currency_by_code_success(db_session):
    from database.model.misc.currency import Currency
    from database.model.core.company import Company

    company = Company(code="TESTCO", name="Test Company")
    db_session.add(company)
    await db_session.commit()

    currency = Currency(code="USD", name="US Dollar", decimals=2, company_id=company.id)
    db_session.add(currency)
    await db_session.commit()

    provider = CurrencyProvider(db_session)
    result = await provider.get_currency_by_code("USD")

    assert result.code == "USD"
    assert result.name == "US Dollar"


@pytest.mark.asyncio
async def test_get_currency_by_code_not_found(db_session):
    provider = CurrencyProvider(db_session)

    with pytest.raises(NotFoundError):
        await provider.get_currency_by_code("XXX")


@pytest.mark.asyncio
async def test_get_currency_by_code_invalid_input(db_session):
    provider = CurrencyProvider(db_session)

    with pytest.raises(ValidationError):
        await provider.get_currency_by_code("")

    with pytest.raises(ValidationError):
        await provider.get_currency_by_code("TOOLONG")


@pytest.mark.asyncio
async def test_list_currencies_success(db_session):
    from database.model.misc.currency import Currency
    from database.model.core.company import Company

    company = Company(code="LISTCO", name="List Company")
    db_session.add(company)
    await db_session.commit()

    currencies = [
        Currency(code="USD", name="US Dollar", decimals=2, company_id=company.id),
        Currency(code="EUR", name="Euro", decimals=2, company_id=company.id),
        Currency(code="ZMW", name="Zambian Kwacha", decimals=2, company_id=company.id),
    ]
    for c in currencies:
        db_session.add(c)
    await db_session.commit()

    provider = CurrencyProvider(db_session)
    results = await provider.list_currencies()

    assert len(results) == 3


@pytest.mark.asyncio
async def test_list_currencies_with_filter(db_session):
    from database.model.misc.currency import Currency
    from database.model.core.company import Company

    company = Company(code="FILTERCO", name="Filter Company")
    db_session.add(company)
    await db_session.commit()

    currencies = [
        Currency(code="USD", name="US Dollar", decimals=2, company_id=company.id),
        Currency(code="EUR", name="Euro", decimals=2, company_id=company.id),
    ]
    for c in currencies:
        db_session.add(c)
    await db_session.commit()

    provider = CurrencyProvider(db_session)
    filter_params = CurrencyProviderFilter(code="USD")  # type: ignore
    results = await provider.list_currencies(filter_params)

    assert len(results) == 1
    assert results[0].code == "USD"


@pytest.mark.asyncio
async def test_list_currencies_with_pagination(db_session):
    from database.model.misc.currency import Currency
    from database.model.core.company import Company

    company = Company(code="PAGECO", name="Page Company")
    db_session.add(company)
    await db_session.commit()

    for i in range(5):
        currency = Currency(
            code=f"CURR{i:03d}",
            name=f"Currency {i}",
            decimals=2,
            company_id=company.id
        )
        db_session.add(currency)
    await db_session.commit()

    provider = CurrencyProvider(db_session)

    filter_params = CurrencyProviderFilter(limit=2, offset=0)  # type: ignore
    results = await provider.list_currencies(filter_params)
    assert len(results) == 2

    filter_params = CurrencyProviderFilter(limit=2, offset=2)  # type: ignore
    results = await provider.list_currencies(filter_params)
    assert len(results) == 2


def test_revalue_balance_success():
    # Create provider with None session - only for pure calculation tests
    provider = CurrencyProvider(None)  # type: ignore

    result = provider.revalue_balance(1000, 2.0, 2.5)
    assert result == 500.00

    result = provider.revalue_balance(1000, 2.5, 2.0)
    assert result == -500.00


def test_revalue_balance_invalid_input():
    provider = CurrencyProvider(None)  # type: ignore

    with pytest.raises(CalculationError):
        provider.revalue_balance(-100, 2.0, 2.5)

    with pytest.raises(CalculationError):
        provider.revalue_balance(1000, 0, 2.5)

    with pytest.raises(CalculationError):
        provider.revalue_balance(1000, -1, 2.5)

    with pytest.raises(CalculationError):
        provider.revalue_balance(1000, 2.0, 0)


@pytest.mark.asyncio
async def test_database_integrity_error_handling(db_session):
    """Test that IntegrityError (duplicate key) is raised correctly."""
    from database.model.misc.currency import Currency
    from database.model.core.company import Company

    company = Company(code="ERRCO", name="Error Company")
    db_session.add(company)
    await db_session.commit()

    # Create first currency
    currency1 = Currency(code="DUPLICATE", name="First", decimals=2, company_id=company.id)
    db_session.add(currency1)
    await db_session.commit()

    # Try to create duplicate currency - this should raise IntegrityError
    currency2 = Currency(code="DUPLICATE", name="Second", decimals=2, company_id=company.id)
    db_session.add(currency2)
    
    with pytest.raises(IntegrityError):
        await db_session.commit()