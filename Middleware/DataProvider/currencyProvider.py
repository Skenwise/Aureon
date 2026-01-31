# Middleware/DataProvider/CurrencyProvider/currencyProvider.py

"""
Currency data provider.
Provides database access for Currency and ExchangeRate models.
Supports deterministic retrieval and FX revaluation operations.
"""

from typing import List, Optional
from sqlmodel import select, Session, col
from sqlalchemy import desc
from database.model.misc.currency import Currency
from database.model.misc.exchange_rate import ExchangeRate
from backend.core.error import NotFoundError, CalculationError
from datetime import datetime


class CurrencyProvider:
    """
    Provider for currency and exchange rate queries.
    Encapsulates all database logic for currency operations and FX lookups.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session (Session): SQLModel session for DB operations.
        """
        self.session = session

    # ----------------- Currency ----------------- #

    def get_currency_by_code(self, code: str) -> Currency:
        """
        Retrieve a currency by its ISO code.

        Args:
            code (str): Currency ISO code.

        Returns:
            Currency: Currency object if found.

        Raises:
            NotFoundError: If no currency with the given code exists.
        """
        stmt = select(Currency).where(Currency.code == code.upper())
        currency = self.session.exec(stmt).first()

        if not currency:
            raise NotFoundError("Currency", code)

        return currency

    def list_currencies(self) -> List[Currency]:
        """
        List all available currencies.

        Returns:
            List[Currency]: All currencies in the system.
        """
        stmt = select(Currency)
        return list(self.session.exec(stmt).all())

    # ----------------- Exchange Rates ----------------- #

    def get_rate(self, base_currency: str, quote_currency: str) -> float:
        """
        Retrieve the latest exchange rate from base to quote currency.

        Args:
            base_currency (str): ISO code of base currency.
            quote_currency (str): ISO code of quote currency.

        Returns:
            float: Conversion rate.

        Raises:
            NotFoundError: If rate not found.
        """
        stmt = (
            select(ExchangeRate)
            .where(ExchangeRate.base_currency == base_currency.upper())
            .where(ExchangeRate.quote_currency == quote_currency.upper())
            .order_by(col(ExchangeRate.valid_from).desc())
        )
        rate_obj = self.session.exec(stmt).first()

        if not rate_obj:
            raise NotFoundError("ExchangeRate", f"{base_currency}->{quote_currency}")

        return rate_obj.rate

    def list_exchange_rates(self) -> List[ExchangeRate]:
        """
        List all exchange rates.

        Returns:
            List[ExchangeRate]: All exchange rates in the system.
        """
        stmt = select(ExchangeRate)
        return list(self.session.exec(stmt).all())

    # ----------------- FX Revaluation ----------------- #

    def revalue_balance(self, balance: float, old_rate: float, new_rate: float) -> float:
        """
        Calculate unrealized gain/loss for a balance given old and new FX rates.

        Args:
            balance (float): Balance amount in foreign currency.
            old_rate (float): Previous FX rate to base currency.
            new_rate (float): Current FX rate to base currency.

        Returns:
            float: Gain (positive) or loss (negative).

        Raises:
            CalculationError: If input values are invalid.
        """
        if old_rate <= 0 or new_rate <= 0:
            raise CalculationError("FX rates must be greater than zero.")

        return round(balance * (new_rate - old_rate), 2)
