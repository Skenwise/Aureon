# backend/currency/fx_revaluation.py

"""
FX Revaluation Port & Adapter.

Calculates unrealized gains/losses for multi-currency balances.
"""

from typing import Protocol
from backend.core.error import CalculationError
from Middleware.DataProvider.currencyProvider import CurrencyProvider


class FXRevaluationPort(Protocol):
    """
    Port interface for FX revaluation operations.
    """

    def revalue_balance(self, balance: float, old_rate: float, new_rate: float) -> float:
        """
        Calculate unrealized gain or loss for a balance given old and new FX rates.

        Args:
            balance (float): Balance amount in foreign currency.
            old_rate (float): Previous FX rate to base currency.
            new_rate (float): Current FX rate to base currency.

        Returns:
            float: Positive value for gain, negative for loss.

        Raises:
            CalculationError: If input values are invalid.
        """
        raise NotImplementedError


class FXRevaluationAdapter(FXRevaluationPort):
    """
    Adapter implementing FXRevaluationPort.

    Delegates FX revaluation calculations to CurrencyProvider.
    """

    def __init__(self, provider: CurrencyProvider):
        """
        Initialize adapter with a currency provider.

        Args:
            provider (CurrencyProvider): Handles calculations and DB access if needed.
        """
        self.provider = provider

    def revalue_balance(self, balance: float, old_rate: float, new_rate: float) -> float:
        """
        Calculate unrealized gain/loss using provider logic.

        Args:
            balance (float): Balance amount in foreign currency.
            old_rate (float): Previous FX rate.
            new_rate (float): Current FX rate.

        Returns:
            float: Positive for gain, negative for loss.

        Raises:
            CalculationError: If input values are invalid.
        """
        return self.provider.revalue_balance(balance, old_rate, new_rate)
