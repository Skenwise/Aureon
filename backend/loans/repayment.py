# backend/loans/repayment.py
"""
Repayment Port & Adapter.
Defines loan repayment operations and delegates to RepaymentProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.loanSchema import RepaymentCreate, RepaymentRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.LoanProvider.repaymentProvider import RepaymentProvider


class RepaymentPort(Protocol):
    """
    Port interface for loan repayment operations.
    All operations coordinate payment receipt, schedule updates, and accounting.
    No provider or infrastructure logic should be handled here.
    """

    def create_repayment(self, repayment_in: RepaymentCreate) -> RepaymentRead:
        """
        Create a repayment record for a loan.
        
        Args:
            repayment_in (RepaymentCreate): Repayment data.
        
        Returns:
            RepaymentRead: Created repayment record with PENDING status.
        
        Raises:
            ValidationError: If loan is not active or payment amount is invalid.
            NotFoundError: If loan does not exist.
        """
        raise NotImplementedError

    def get_repayment(self, repayment_id: UUID) -> RepaymentRead:
        """
        Retrieve a repayment by its ID.
        
        Args:
            repayment_id (UUID): Repayment identifier.
        
        Returns:
            RepaymentRead: Repayment details.
        
        Raises:
            NotFoundError: If the repayment does not exist.
        """
        raise NotImplementedError

    def list_repayments(self, loan_id: UUID) -> List[RepaymentRead]:
        """
        List all repayments for a specific loan.
        
        Args:
            loan_id (UUID): Loan identifier.
        
        Returns:
            List[RepaymentRead]: All repayments for the loan.
        """
        raise NotImplementedError

    def apply_repayment(self, repayment_id: UUID) -> RepaymentRead:
        """
        Apply a repayment to the loan.
        Coordinates: Payments → Accounting → Schedule Update → Loan Balance Update.
        
        Args:
            repayment_id (UUID): Repayment identifier.
        
        Returns:
            RepaymentRead: Updated repayment with APPLIED status.
        
        Raises:
            NotFoundError: If the repayment does not exist.
            ValidationError: If repayment already applied.
        """
        raise NotImplementedError

    def reverse_repayment(self, repayment_id: UUID, reason: str) -> RepaymentRead:
        """
        Reverse a previously applied repayment.
        
        Args:
            repayment_id (UUID): Repayment identifier.
            reason (str): Reversal reason.
        
        Returns:
            RepaymentRead: Updated repayment with REVERSED status.
        
        Raises:
            NotFoundError: If the repayment does not exist.
            ValidationError: If repayment cannot be reversed.
        """
        raise NotImplementedError


class RepaymentAdapter(RepaymentPort):
    """
    Adapter implementation of RepaymentPort.
    Delegates all repayment operations to RepaymentProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: RepaymentProvider):
        """
        Initialize the adapter with a repayment provider.
        
        Args:
            provider (RepaymentProvider): The data provider for repayment operations.
        """
        self.provider = provider

    def create_repayment(self, repayment_in: RepaymentCreate) -> RepaymentRead:
        """
        Create repayment via provider implementation.
        """
        repayment_model = self.provider.create_repayment(cast(Any, repayment_in))
        return RepaymentRead.model_validate(repayment_model)

    def get_repayment(self, repayment_id: UUID) -> RepaymentRead:
        """
        Retrieve repayment via provider implementation.
        """
        repayment_model = self.provider.get_repayment(repayment_id)
        return RepaymentRead.model_validate(repayment_model)

    def list_repayments(self, loan_id: UUID) -> List[RepaymentRead]:
        """
        List repayments via provider implementation.
        """
        repayments = self.provider.list_repayments(loan_id)
        return [RepaymentRead.model_validate(r) for r in repayments]

    def apply_repayment(self, repayment_id: UUID) -> RepaymentRead:
        """
        Apply repayment via provider implementation.
        Provider coordinates with payments, accounting, and schedule.
        """
        repayment_model = self.provider.apply_repayment(repayment_id)
        return RepaymentRead.model_validate(repayment_model)

    def reverse_repayment(self, repayment_id: UUID, reason: str) -> RepaymentRead:
        """
        Reverse repayment via provider implementation.
        """
        repayment_model = self.provider.reverse_repayment(repayment_id, reason)
        return RepaymentRead.model_validate(repayment_model)