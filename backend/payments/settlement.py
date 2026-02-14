# backend/payments/settlement.py
"""
Settlement Port & Adapter.
Defines internal settlement operations and delegates to SettlementProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.paymentSchema import SettlementCreate, SettlementRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.PaymentProvider.settlementProvider import SettlementProvider


class SettlementPort(Protocol):
    """
    Port interface for settlement operations.
    All operations handle internal money movement within Aureon.
    No provider or infrastructure logic should be handled here.
    """

    def create_settlement(self, settlement_in: SettlementCreate) -> SettlementRead:
        """
        Create an internal settlement.
        
        Args:
            settlement_in (SettlementCreate): Input data for settlement creation.
        
        Returns:
            SettlementRead: The created settlement record.
        
        Raises:
            ValidationError: If settlement data is invalid or insufficient funds.
        """
        raise NotImplementedError

    def get_settlement(self, settlement_id: UUID) -> SettlementRead:
        """
        Retrieve a settlement by its unique ID.
        
        Args:
            settlement_id (UUID): Settlement identifier.
        
        Returns:
            SettlementRead: Settlement details.
        
        Raises:
            NotFoundError: If the settlement does not exist.
        """
        raise NotImplementedError

    def get_settlement_by_number(self, payment_number: str) -> SettlementRead:
        """
        Retrieve a settlement by its payment number.
        
        Args:
            payment_number (str): Unique payment number.
        
        Returns:
            SettlementRead: Settlement details.
        
        Raises:
            NotFoundError: If the settlement does not exist.
        """
        raise NotImplementedError

    def list_settlements(
        self, 
        account_id: UUID | None = None,
        settlement_type: str | None = None,
        status: str | None = None
    ) -> List[SettlementRead]:
        """
        List all settlements, optionally filtered.
        
        Args:
            account_id (UUID, optional): Filter by source or destination account.
            settlement_type (str, optional): Filter by settlement type.
            status (str, optional): Filter by settlement status.
        
        Returns:
            List[SettlementRead]: All matching settlement records.
        """
        raise NotImplementedError

    def execute_settlement(self, settlement_id: UUID) -> SettlementRead:
        """
        Execute a pending settlement.
        Coordinates: Internal Provider → Accounting (no external network).
        
        Args:
            settlement_id (UUID): Settlement identifier.
        
        Returns:
            SettlementRead: Updated settlement with execution status.
        
        Raises:
            NotFoundError: If the settlement does not exist.
            ValidationError: If settlement cannot be executed.
        """
        raise NotImplementedError

    def reverse_settlement(self, settlement_id: UUID, reason: str) -> SettlementRead:
        """
        Reverse a completed settlement.
        
        Args:
            settlement_id (UUID): Settlement identifier.
            reason (str): Reversal reason.
        
        Returns:
            SettlementRead: Updated settlement with REVERSED status.
        
        Raises:
            NotFoundError: If the settlement does not exist.
            ValidationError: If settlement cannot be reversed.
        """
        raise NotImplementedError


class SettlementAdapter(SettlementPort):
    """
    Adapter implementation of SettlementPort.
    Delegates all settlement operations to SettlementProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: SettlementProvider):
        """
        Initialize the adapter with a settlement provider.
        
        Args:
            provider (SettlementProvider): The data provider for settlement operations.
        """
        self.provider = provider

    def create_settlement(self, settlement_in: SettlementCreate) -> SettlementRead:
        """
        Create settlement via provider implementation.
        """
        settlement_model = self.provider.create_settlement(cast(Any, settlement_in))
        return SettlementRead.model_validate(settlement_model)

    def get_settlement(self, settlement_id: UUID) -> SettlementRead:
        """
        Retrieve settlement by ID via provider implementation.
        """
        settlement_model = self.provider.get_settlement(settlement_id)
        return SettlementRead.model_validate(settlement_model)

    def get_settlement_by_number(self, payment_number: str) -> SettlementRead:
        """
        Retrieve settlement by payment number via provider implementation.
        """
        settlement_model = self.provider.get_settlement_by_number(payment_number)
        return SettlementRead.model_validate(settlement_model)

    def list_settlements(
        self, 
        account_id: UUID | None = None,
        settlement_type: str | None = None,
        status: str | None = None
    ) -> List[SettlementRead]:
        """
        List settlements via provider, optionally filtered.
        """
        settlements = self.provider.list_settlements(account_id, settlement_type, status)
        return [SettlementRead.model_validate(settlement) for settlement in settlements]

    def execute_settlement(self, settlement_id: UUID) -> SettlementRead:
        """
        Execute settlement via provider implementation.
        Provider coordinates with internal execution provider and accounting.
        """
        settlement_model = self.provider.execute_settlement(settlement_id)
        return SettlementRead.model_validate(settlement_model)

    def reverse_settlement(self, settlement_id: UUID, reason: str) -> SettlementRead:
        """
        Reverse settlement via provider implementation.
        """
        settlement_model = self.provider.reverse_settlement(settlement_id, reason)
        return SettlementRead.model_validate(settlement_model)