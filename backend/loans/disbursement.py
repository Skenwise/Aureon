# backend/loans/disbursement.py
"""
Disbursement Port & Adapter.
Defines loan disbursement operations and delegates to DisbursementProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.loanSchema import DisbursementCreate, DisbursementRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.LoanProvider.disbursementProvider import DisbursementProvider


class DisbursementPort(Protocol):
    """
    Port interface for loan disbursement operations.
    All operations coordinate fund transfer, treasury, and accounting.
    No provider or infrastructure logic should be handled here.
    """

    def create_disbursement(self, disbursement_in: DisbursementCreate) -> DisbursementRead:
        """
        Create a disbursement record for a loan.
        
        Args:
            disbursement_in (DisbursementCreate): Disbursement request data.
        
        Returns:
            DisbursementRead: Created disbursement record with PENDING status.
        
        Raises:
            ValidationError: If loan is not in correct status or amount exceeds principal.
            NotFoundError: If loan does not exist.
        """
        raise NotImplementedError

    def get_disbursement(self, disbursement_id: UUID) -> DisbursementRead:
        """
        Retrieve a disbursement by its ID.
        
        Args:
            disbursement_id (UUID): Disbursement identifier.
        
        Returns:
            DisbursementRead: Disbursement details.
        
        Raises:
            NotFoundError: If the disbursement does not exist.
        """
        raise NotImplementedError

    def list_disbursements(self, loan_id: UUID) -> List[DisbursementRead]:
        """
        List all disbursements for a specific loan.
        
        Args:
            loan_id (UUID): Loan identifier.
        
        Returns:
            List[DisbursementRead]: All disbursements for the loan.
        """
        raise NotImplementedError

    def execute_disbursement(self, disbursement_id: UUID) -> DisbursementRead:
        """
        Execute a pending disbursement.
        Coordinates: Treasury → Payments → Accounting → Loan Status Update.
        
        Args:
            disbursement_id (UUID): Disbursement identifier.
        
        Returns:
            DisbursementRead: Updated disbursement with COMPLETED status.
        
        Raises:
            NotFoundError: If the disbursement does not exist.
            ValidationError: If insufficient treasury funds or disbursement already executed.
        """
        raise NotImplementedError

    def fail_disbursement(self, disbursement_id: UUID, reason: str) -> DisbursementRead:
        """
        Mark a disbursement as failed.
        
        Args:
            disbursement_id (UUID): Disbursement identifier.
            reason (str): Failure reason.
        
        Returns:
            DisbursementRead: Updated disbursement with FAILED status.
        
        Raises:
            NotFoundError: If the disbursement does not exist.
        """
        raise NotImplementedError


class DisbursementAdapter(DisbursementPort):
    """
    Adapter implementation of DisbursementPort.
    Delegates all disbursement operations to DisbursementProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: DisbursementProvider):
        """
        Initialize the adapter with a disbursement provider.
        
        Args:
            provider (DisbursementProvider): The data provider for disbursement operations.
        """
        self.provider = provider

    def create_disbursement(self, disbursement_in: DisbursementCreate) -> DisbursementRead:
        """
        Create disbursement via provider implementation.
        """
        disbursement_model = self.provider.create_disbursement(cast(Any, disbursement_in))
        return DisbursementRead.model_validate(disbursement_model)

    def get_disbursement(self, disbursement_id: UUID) -> DisbursementRead:
        """
        Retrieve disbursement via provider implementation.
        """
        disbursement_model = self.provider.get_disbursement(disbursement_id)
        return DisbursementRead.model_validate(disbursement_model)

    def list_disbursements(self, loan_id: UUID) -> List[DisbursementRead]:
        """
        List disbursements via provider implementation.
        """
        disbursements = self.provider.list_disbursements(loan_id)
        return [DisbursementRead.model_validate(d) for d in disbursements]

    def execute_disbursement(self, disbursement_id: UUID) -> DisbursementRead:
        """
        Execute disbursement via provider implementation.
        Provider coordinates with treasury, payments, and accounting.
        """
        disbursement_model = self.provider.execute_disbursement(disbursement_id)
        return DisbursementRead.model_validate(disbursement_model)

    def fail_disbursement(self, disbursement_id: UUID, reason: str) -> DisbursementRead:
        """
        Fail disbursement via provider implementation.
        """
        disbursement_model = self.provider.fail_disbursement(disbursement_id, reason)
        return DisbursementRead.model_validate(disbursement_model)