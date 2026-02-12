# backend/treasury/funding.py
"""
Funding Port & Adapter.
Defines treasury funding operations and delegates to provider implementations.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.treasurySchema import FundingTransferCreate, FundingTransferRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.treasuryProvider.FundingProvider import FundingProvider


class FundingPort(Protocol):
    """
    Port interface for funding transfer operations.
    All operations handle movement of funds between provider accounts.
    No provider or infrastructure logic should be handled here.
    """

    def create_transfer(self, transfer_in: FundingTransferCreate) -> FundingTransferRead:
        """
        Create a funding transfer between provider accounts.
        Moves funds from one provider to another (e.g., Bank → MTN).
        
        Args:
            transfer_in (FundingTransferCreate): Transfer request data.
        
        Returns:
            FundingTransferRead: Created transfer record with PENDING status.
        
        Raises:
            ValidationError: If insufficient funds, invalid providers, or currency mismatch.
        """
        raise NotImplementedError

    def get_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Retrieve a funding transfer by its unique ID.
        
        Args:
            transfer_id (str): Unique transfer identifier.
        
        Returns:
            FundingTransferRead: Transfer record with current status.
        
        Raises:
            NotFoundError: If the transfer does not exist.
        """
        raise NotImplementedError

    def list_transfers(
        self, 
        provider: str | None = None,
        status: str | None = None
    ) -> List[FundingTransferRead]:
        """
        List funding transfers, optionally filtered by provider or status.
        
        Args:
            provider (str, optional): Filter by source or destination provider.
            status (str, optional): Filter by transfer status (PENDING, COMPLETED, FAILED, CANCELLED).
        
        Returns:
            List[FundingTransferRead]: All matching transfer records.
        """
        raise NotImplementedError

    def complete_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Mark a transfer as completed after successful execution.
        Updates status to COMPLETED and records completion timestamp.
        
        Args:
            transfer_id (str): Unique transfer identifier.
        
        Returns:
            FundingTransferRead: Updated transfer record with COMPLETED status.
        
        Raises:
            NotFoundError: If the transfer does not exist.
            ValidationError: If transfer is not in PENDING status.
        """
        raise NotImplementedError

    def fail_transfer(self, transfer_id: str, reason: str) -> FundingTransferRead:
        """
        Mark a transfer as failed with error reason.
        
        Args:
            transfer_id (str): Unique transfer identifier.
            reason (str): Failure reason description.
        
        Returns:
            FundingTransferRead: Updated transfer record with FAILED status.
        
        Raises:
            NotFoundError: If the transfer does not exist.
        """
        raise NotImplementedError

    def cancel_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Cancel a pending transfer before execution.
        
        Args:
            transfer_id (str): Unique transfer identifier.
        
        Returns:
            FundingTransferRead: Updated transfer record with CANCELLED status.
        
        Raises:
            NotFoundError: If the transfer does not exist.
            ValidationError: If transfer is not in PENDING status.
        """
        raise NotImplementedError


class FundingAdapter(FundingPort):
    """
    Adapter implementation of FundingPort.
    Delegates all funding transfer operations to FundingProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: FundingProvider):
        """
        Initialize the adapter with a funding provider.
        
        Args:
            provider (FundingProvider): The data provider for funding operations.
        """
        self.provider = provider

    def create_transfer(self, transfer_in: FundingTransferCreate) -> FundingTransferRead:
        """
        Create a funding transfer via provider implementation.
        """
        transfer_model = self.provider.create_transfer(cast(Any, transfer_in))
        return FundingTransferRead.model_validate(transfer_model)

    def get_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Retrieve transfer by ID via provider implementation.
        """
        transfer_model = self.provider.get_transfer(transfer_id)
        return FundingTransferRead.model_validate(transfer_model)

    def list_transfers(
        self, 
        provider: str | None = None,
        status: str | None = None
    ) -> List[FundingTransferRead]:
        """
        List transfers via provider, optionally filtered.
        """
        transfers = self.provider.list_transfers(provider, status)
        return [FundingTransferRead.model_validate(t) for t in transfers]

    def complete_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Mark transfer as completed via provider implementation.
        """
        transfer_model = self.provider.complete_transfer(transfer_id)
        return FundingTransferRead.model_validate(transfer_model)

    def fail_transfer(self, transfer_id: str, reason: str) -> FundingTransferRead:
        """
        Mark transfer as failed via provider implementation.
        """
        transfer_model = self.provider.fail_transfer(transfer_id, reason)
        return FundingTransferRead.model_validate(transfer_model)

    def cancel_transfer(self, transfer_id: str) -> FundingTransferRead:
        """
        Cancel transfer via provider implementation.
        """
        transfer_model = self.provider.cancel_transfer(transfer_id)
        return FundingTransferRead.model_validate(transfer_model)