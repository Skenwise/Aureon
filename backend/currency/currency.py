# backend/currency/currency.py

"""
Currency Port & Adapter.

Defines core currency operations and delegates to CurrencyProvider.
"""

from typing import List, Protocol
from schemas.currencySchema import CurrencyRead
from backend.core.error import NotFoundError
from Middleware.DataProvider.currencyProvider import CurrencyProvider


class CurrencyPort(Protocol):
    """
    Port interface for currency operations.

    All operations are deterministic and validated.
    """

    def get_currency_by_code(self, code: str) -> CurrencyRead:
        """
        Retrieve a currency by its ISO code.

        Args:
            code (str): Currency ISO code.

        Returns:
            CurrencyRead: Currency representation.

        Raises:
            NotFoundError: If the currency does not exist.
        """
        raise NotImplementedError

    def list_currencies(self) -> List[CurrencyRead]:
        """
        List all available currencies.

        Returns:
            List[CurrencyRead]: List of all supported currencies.
        """
        raise NotImplementedError


class CurrencyAdapter(CurrencyPort):
    """
    Adapter implementing CurrencyPort.

    Delegates currency retrieval operations to CurrencyProvider.
    """

    def __init__(self, provider: CurrencyProvider):
        """
        Initialize the adapter with a currency provider.

        Args:
            provider (CurrencyProvider): Handles database queries and calculations for currencies.
        """
        self.provider = provider

    def get_currency_by_code(self, code: str) -> CurrencyRead:
        """
        Retrieve a currency by ISO code using the provider.

        Args:
            code (str): Currency ISO code.

        Returns:
            CurrencyRead: Currency representation.

        Raises:
            NotFoundError: If the currency is not found.
        """
        currency = self.provider.get_currency_by_code(code)
        return CurrencyRead.model_validate(currency)

    def list_currencies(self) -> List[CurrencyRead]:
        """
        Retrieve all supported currencies using the provider.

        Returns:
            List[CurrencyRead]: List of all currency representations.
        """
        currencies = self.provider.list_currencies()
        return [CurrencyRead.model_validate(c) for c in currencies]
