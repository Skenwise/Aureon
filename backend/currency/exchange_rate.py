# backend/currency/exchange_rate.py

"""
Exchange Rate Port & Adapter.

Handles FX rate retrieval and currency conversions, delegating to CurrencyProvider.
"""

from typing import Protocol
from backend.core.error import NotFoundError
from Middleware.DataProvider.currencyProvider import CurrencyProvider


class ExchangeRatePort(Protocol):
    """
    Port interface for exchange rate operations.
    """

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Retrieve the exchange rate from one currency to another.

        Args:
            from_currency (str): ISO code of source currency.
            to_currency (str): ISO code of target currency.

        Returns:
            float: Conversion rate.

        Raises:
            NotFoundError: If rate is not found.
        """
        raise NotImplementedError

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert an amount between two currencies using the exchange rate.

        Args:
            amount (float): Amount to convert.
            from_currency (str): ISO code of source currency.
            to_currency (str): ISO code of target currency.

        Returns:
            float: Converted amount.

        Raises:
            NotFoundError: If exchange rate is not found.
        """
        raise NotImplementedError


class ExchangeRateAdapter(ExchangeRatePort):
    """
    Adapter implementing ExchangeRatePort.

    Delegates FX rate retrieval and conversion to CurrencyProvider.
    """

    def __init__(self, provider: CurrencyProvider):
        """
        Initialize adapter with a currency provider.

        Args:
            provider (CurrencyProvider): Handles DB queries and conversion logic.
        """
        self.provider = provider

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Retrieve the exchange rate between two currencies.

        Args:
            from_currency (str): ISO code of source currency.
            to_currency (str): ISO code of target currency.

        Returns:
            float: Conversion rate.

        Raises:
            NotFoundError: If rate does not exist.
        """
        return self.provider.get_rate(from_currency, to_currency)

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert an amount between currencies using the provider.

        Args:
            amount (float): Amount to convert.
            from_currency (str): ISO code of source currency.
            to_currency (str): ISO code of target currency.

        Returns:
            float: Converted amount.

        Raises:
            NotFoundError: If exchange rate is not found.
        """
        rate = self.get_rate(from_currency, to_currency)
        return amount * rate
