# backend/treasury/cash_positions.py
"""
Cash Position Port & Adapter.
Defines treasury cash position operations and delegates to provider implementations.
"""
from typing import List, Protocol, Any, cast
from datetime import datetime
from decimal import Decimal
from schemas.treasurySchema import (
    CashPositionRead,
    ProviderBalanceRead,
    ReserveFundsCreate,
    ReserveFundsRead
)
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.treasuryProvider.cashPositionProvider import CashPositionProvider


class CashPositionPort(Protocol):
    """
    Port interface for cash position operations.
    All operations track real-time liquidity across providers.
    No provider or infrastructure logic should be handled here.
    """

    def fetch_balance(self, provider: str, account_id: str) -> ProviderBalanceRead:
        """
        Fetch current balance from an external provider API.
        
        Args:
            provider (str): Provider identifier (e.g., 'MTN', 'AIRTEL', 'BANK_ABC').
            account_id (str): Account identifier within the provider.
        
        Returns:
            ProviderBalanceRead: Raw balance data from provider API.
        
        Raises:
            NotFoundError: If the provider or account does not exist.
            ValidationError: If provider API returns invalid data.
        """
        raise NotImplementedError

    def get_cash_position(self, provider: str, account_id: str) -> CashPositionRead:
        """
        Get normalized cash position for a specific provider account.
        Includes total, available, and reserved balances.
        
        Args:
            provider (str): Provider identifier.
            account_id (str): Account identifier.
        
        Returns:
            CashPositionRead: Normalized cash position snapshot.
        
        Raises:
            NotFoundError: If the cash position does not exist.
        """
        raise NotImplementedError

    def list_cash_positions(
        self, 
        currency_code: str | None = None
    ) -> List[CashPositionRead]:
        """
        List all cash positions, optionally filtered by currency.
        
        Args:
            currency_code (str, optional): Filter by ISO 4217 currency code.
        
        Returns:
            List[CashPositionRead]: All matching cash positions.
        """
        raise NotImplementedError

    def reserve_funds(self, reserve_in: ReserveFundsCreate) -> ReserveFundsRead:
        """
        Reserve funds in a provider account for a pending transaction.
        Reduces available balance without moving actual money.
        
        Args:
            reserve_in (ReserveFundsCreate): Reservation request data.
        
        Returns:
            ReserveFundsRead: Created reservation record.
        
        Raises:
            ValidationError: If insufficient funds or invalid reservation data.
        """
        raise NotImplementedError

    def release_reservation(self, reservation_id: str) -> ReserveFundsRead:
        """
        Release a fund reservation, making funds available again.
        
        Args:
            reservation_id (str): Unique reservation identifier.
        
        Returns:
            ReserveFundsRead: Updated reservation record with RELEASED status.
        
        Raises:
            NotFoundError: If the reservation does not exist.
        """
        raise NotImplementedError

    def confirm_reservation(self, reservation_id: str) -> ReserveFundsRead:
        """
        Confirm a fund reservation after successful transaction execution.
        Marks funds as permanently consumed.
        
        Args:
            reservation_id (str): Unique reservation identifier.
        
        Returns:
            ReserveFundsRead: Updated reservation record with CONFIRMED status.
        
        Raises:
            NotFoundError: If the reservation does not exist.
        """
        raise NotImplementedError


class CashPositionAdapter(CashPositionPort):
    """
    Adapter implementation of CashPositionPort.
    Delegates all cash position operations to CashPositionProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: CashPositionProvider):
        """
        Initialize the adapter with a provider.
        
        Args:
            provider (CashPositionProvider): The data provider for cash position operations.
        """
        self.provider = provider

    def fetch_balance(self, provider: str, account_id: str) -> ProviderBalanceRead:
        """
        Fetch current balance from external provider API via provider implementation.
        """
        balance_model = self.provider.fetch_balance(provider, account_id)
        return ProviderBalanceRead.model_validate(balance_model)

    def get_cash_position(self, provider: str, account_id: str) -> CashPositionRead:
        """
        Retrieve normalized cash position via provider implementation.
        """
        position_model = self.provider.get_cash_position(provider, account_id)
        return CashPositionRead.model_validate(position_model)

    def list_cash_positions(
        self, 
        currency_code: str | None = None
    ) -> List[CashPositionRead]:
        """
        List all cash positions via provider, optionally filtered by currency.
        """
        positions = self.provider.list_cash_positions(currency_code)
        return [CashPositionRead.model_validate(p) for p in positions]

    def reserve_funds(self, reserve_in: ReserveFundsCreate) -> ReserveFundsRead:
        """
        Create fund reservation via provider implementation.
        """
        reservation_model = self.provider.reserve_funds(cast(Any, reserve_in))
        return ReserveFundsRead.model_validate(reservation_model)

    def release_reservation(self, reservation_id: str) -> ReserveFundsRead:
        """
        Release fund reservation via provider implementation.
        """
        reservation_model = self.provider.release_reservation(reservation_id)
        return ReserveFundsRead.model_validate(reservation_model)

    def confirm_reservation(self, reservation_id: str) -> ReserveFundsRead:
        """
        Confirm fund reservation via provider implementation.
        """
        reservation_model = self.provider.confirm_reservation(reservation_id)
        return ReserveFundsRead.model_validate(reservation_model)