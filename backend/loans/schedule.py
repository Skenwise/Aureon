# backend/loans/schedule.py
"""
Schedule Port & Adapter.
Defines loan repayment schedule operations and delegates to ScheduleProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.loanSchema import ScheduleCreate, ScheduleRead, ScheduleInstallmentRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.LoanProvider.scheduleProvider import ScheduleProvider


class SchedulePort(Protocol):
    """
    Port interface for loan schedule operations.
    All operations define repayment timelines, not payment execution.
    No provider or infrastructure logic should be handled here.
    """

    def generate_schedule(self, schedule_in: ScheduleCreate) -> ScheduleRead:
        """
        Generate a complete repayment schedule for a loan.
        
        Args:
            schedule_in (ScheduleCreate): Schedule generation parameters.
        
        Returns:
            ScheduleRead: Complete repayment schedule with all installments.
        
        Raises:
            ValidationError: If schedule parameters are invalid.
            NotFoundError: If the loan does not exist.
        """
        raise NotImplementedError

    def get_schedule(self, loan_id: UUID) -> ScheduleRead:
        """
        Retrieve the complete schedule for a loan.
        
        Args:
            loan_id (UUID): Loan identifier.
        
        Returns:
            ScheduleRead: Complete repayment schedule.
        
        Raises:
            NotFoundError: If the schedule does not exist.
        """
        raise NotImplementedError

    def get_installment(self, installment_id: UUID) -> ScheduleInstallmentRead:
        """
        Retrieve a single schedule installment.
        
        Args:
            installment_id (UUID): Installment identifier.
        
        Returns:
            ScheduleInstallmentRead: Installment details.
        
        Raises:
            NotFoundError: If the installment does not exist.
        """
        raise NotImplementedError

    def get_next_due_installment(self, loan_id: UUID) -> ScheduleInstallmentRead | None:
        """
        Get the next unpaid installment for a loan.
        
        Args:
            loan_id (UUID): Loan identifier.
        
        Returns:
            ScheduleInstallmentRead | None: Next due installment or None if all paid.
        """
        raise NotImplementedError

    def update_installment_status(
        self, 
        installment_id: UUID, 
        status: str,
        paid_amount: float | None = None
    ) -> ScheduleInstallmentRead:
        """
        Update installment status after payment application.
        
        Args:
            installment_id (UUID): Installment identifier.
            status (str): New status (PAID, PARTIALLY_PAID, OVERDUE).
            paid_amount (float, optional): Amount paid toward this installment.
        
        Returns:
            ScheduleInstallmentRead: Updated installment.
        
        Raises:
            NotFoundError: If the installment does not exist.
        """
        raise NotImplementedError


class ScheduleAdapter(SchedulePort):
    """
    Adapter implementation of SchedulePort.
    Delegates all schedule operations to ScheduleProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: ScheduleProvider):
        """
        Initialize the adapter with a schedule provider.
        
        Args:
            provider (ScheduleProvider): The data provider for schedule operations.
        """
        self.provider = provider

    def generate_schedule(self, schedule_in: ScheduleCreate) -> ScheduleRead:
        """
        Generate schedule via provider implementation.
        """
        schedule_model = self.provider.generate_schedule(cast(Any, schedule_in))
        return ScheduleRead.model_validate(schedule_model)

    def get_schedule(self, loan_id: UUID) -> ScheduleRead:
        """
        Retrieve schedule via provider implementation.
        """
        schedule_model = self.provider.get_schedule(loan_id)
        return ScheduleRead.model_validate(schedule_model)

    def get_installment(self, installment_id: UUID) -> ScheduleInstallmentRead:
        """
        Retrieve installment via provider implementation.
        """
        installment_model = self.provider.get_installment(installment_id)
        return ScheduleInstallmentRead.model_validate(installment_model)

    def get_next_due_installment(self, loan_id: UUID) -> ScheduleInstallmentRead | None:
        """
        Get next due installment via provider implementation.
        """
        installment_model = self.provider.get_next_due_installment(loan_id)
        if installment_model is None:
            return None
        return ScheduleInstallmentRead.model_validate(installment_model)

    def update_installment_status(
        self, 
        installment_id: UUID, 
        status: str,
        paid_amount: float | None = None
    ) -> ScheduleInstallmentRead:
        """
        Update installment status via provider implementation.
        """
        installment_model = self.provider.update_installment_status(
            installment_id, status, paid_amount
        )
        return ScheduleInstallmentRead.model_validate(installment_model)