# backend/treasury/liquidity.py
"""
Liquidity Port & Adapter.
Defines treasury liquidity operations and delegates to provider implementations.
"""
from typing import List, Protocol, Any, cast
from datetime import datetime
from decimal import Decimal
from schemas.treasurySchema import LiquidityRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.treasuryProvider.LiquidityProvider import LiquidityProvider


class LiquidityPort(Protocol):
    """
    Port interface for liquidity operations.
    All operations aggregate cash positions across providers to determine
    total available funds. No provider or infrastructure logic should be handled here.
    """

    def get_liquidity(self, currency_code: str) -> LiquidityRead:
        """
        Get aggregated liquidity status for a specific currency.
        Sums total available, reserved, and balance across all providers.
        
        Args:
            currency_code (str): ISO 4217 currency code (e.g., 'ZMW', 'USD').
        
        Returns:
            LiquidityRead: Aggregated liquidity snapshot with provider breakdown.
        
        Raises:
            NotFoundError: If no cash positions exist for the currency.
            ValidationError: If currency code is invalid.
        """
        raise NotImplementedError

    def get_total_liquidity(self) -> List[LiquidityRead]:
        """
        Get aggregated liquidity status for all currencies.
        Returns one LiquidityRead per currency with active cash positions.
        
        Returns:
            List[LiquidityRead]: Liquidity snapshots for each currency.
        """
        raise NotImplementedError

    def check_sufficient_funds(
        self, 
        currency_code: str, 
        required_amount: Decimal
    ) -> bool:
        """
        Check if sufficient available funds exist for a transaction.
        
        Args:
            currency_code (str): ISO 4217 currency code.
            required_amount (Decimal): Amount required for transaction.
        
        Returns:
            bool: True if total available funds >= required amount, False otherwise.
        
        Raises:
            ValidationError: If currency code is invalid or amount is negative.
        """
        raise NotImplementedError


class LiquidityAdapter(LiquidityPort):
    """
    Adapter implementation of LiquidityPort.
    Delegates all liquidity operations to LiquidityProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: LiquidityProvider):
        """
        Initialize the adapter with a liquidity provider.
        
        Args:
            provider (LiquidityProvider): The data provider for liquidity operations.
        """
        self.provider = provider

    def get_liquidity(self, currency_code: str) -> LiquidityRead:
        """
        Retrieve aggregated liquidity for a specific currency via provider.
        """
        liquidity_model = self.provider.get_liquidity(currency_code)
        return LiquidityRead.model_validate(liquidity_model)

    def get_total_liquidity(self) -> List[LiquidityRead]:
        """
        Retrieve aggregated liquidity for all currencies via provider.
        """
        liquidity_models = self.provider.get_total_liquidity()
        return [LiquidityRead.model_validate(liq) for liq in liquidity_models]

    def check_sufficient_funds(
        self, 
        currency_code: str, 
        required_amount: Decimal
    ) -> bool:
        """
        Check fund sufficiency via provider implementation.
        """
        return self.provider.check_sufficient_funds(currency_code, required_amount)