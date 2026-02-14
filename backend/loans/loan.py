# backend/loans/loan.py
"""
Loan Port & Adapter.
Defines core loan contract operations and delegates to LoanProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.loanSchema import LoanCreate, LoanUpdate, LoanRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.LoanProvider.loanProvider import LoanProvider


class LoanPort(Protocol):
    """
    Port interface for loan contract operations.
    All operations define credit obligations, not financial execution.
    No provider or infrastructure logic should be handled here.
    """

    def create_loan(self, loan_in: LoanCreate) -> LoanRead:
        """
        Create a new loan contract.
        
        Args:
            loan_in (LoanCreate): Input data for loan creation.
        
        Returns:
            LoanRead: The created loan contract.
        
        Raises:
            ValidationError: If loan terms are invalid or borrower does not exist.
        """
        raise NotImplementedError

    def get_loan(self, loan_id: UUID) -> LoanRead:
        """
        Retrieve a loan by its unique ID.
        
        Args:
            loan_id (UUID): Loan identifier.
        
        Returns:
            LoanRead: Loan contract details.
        
        Raises:
            NotFoundError: If the loan does not exist.
        """
        raise NotImplementedError

    def get_loan_by_number(self, loan_number: str) -> LoanRead:
        """
        Retrieve a loan by its loan number.
        
        Args:
            loan_number (str): Unique loan number.
        
        Returns:
            LoanRead: Loan contract details.
        
        Raises:
            NotFoundError: If the loan does not exist.
        """
        raise NotImplementedError

    def list_loans(
        self, 
        borrower_id: UUID | None = None,
        status: str | None = None
    ) -> List[LoanRead]:
        """
        List all loans, optionally filtered by borrower or status.
        
        Args:
            borrower_id (UUID, optional): Filter by borrower customer ID.
            status (str, optional): Filter by loan status.
        
        Returns:
            List[LoanRead]: All matching loan contracts.
        """
        raise NotImplementedError

    def update_loan_status(self, loan_id: UUID, status: str) -> LoanRead:
        """
        Update loan status (state machine transition).
        
        Args:
            loan_id (UUID): Loan identifier.
            status (str): New status (PENDING, DISBURSED, ACTIVE, CLOSED, DEFAULTED).
        
        Returns:
            LoanRead: Updated loan contract.
        
        Raises:
            NotFoundError: If the loan does not exist.
            ValidationError: If status transition is invalid.
        """
        raise NotImplementedError


class LoanAdapter(LoanPort):
    """
    Adapter implementation of LoanPort.
    Delegates all loan contract operations to LoanProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: LoanProvider):
        """
        Initialize the adapter with a loan provider.
        
        Args:
            provider (LoanProvider): The data provider for loan operations.
        """
        self.provider = provider

    def create_loan(self, loan_in: LoanCreate) -> LoanRead:
        """
        Create a new loan contract via provider implementation.
        """
        loan_model = self.provider.create_loan(cast(Any, loan_in))
        return LoanRead.model_validate(loan_model)

    def get_loan(self, loan_id: UUID) -> LoanRead:
        """
        Retrieve loan by ID via provider implementation.
        """
        loan_model = self.provider.get_loan(loan_id)
        return LoanRead.model_validate(loan_model)

    def get_loan_by_number(self, loan_number: str) -> LoanRead:
        """
        Retrieve loan by loan number via provider implementation.
        """
        loan_model = self.provider.get_loan_by_number(loan_number)
        return LoanRead.model_validate(loan_model)

    def list_loans(
        self, 
        borrower_id: UUID | None = None,
        status: str | None = None
    ) -> List[LoanRead]:
        """
        List loans via provider, optionally filtered.
        """
        loans = self.provider.list_loans(borrower_id, status)
        return [LoanRead.model_validate(loan) for loan in loans]

    def update_loan_status(self, loan_id: UUID, status: str) -> LoanRead:
        """
        Update loan status via provider implementation.
        """
        loan_model = self.provider.update_loan_status(loan_id, status)
        return LoanRead.model_validate(loan_model)