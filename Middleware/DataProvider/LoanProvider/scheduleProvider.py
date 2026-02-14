# Middleware/DataProvider/LoanProvider/scheduleProvider.py
"""
Schedule Data Provider.

Handles persistence and retrieval of LoanSchedule records.

This provider generates and manages repayment schedules.
It does NOT process payments.
It only manages schedule state.
"""

from typing import List, Optional, cast
from uuid import UUID
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select
from sqlalchemy.sql.elements import ColumnElement

from database.model.finance.loan_schedule import LoanSchedule
from database.model.finance.loan import Loan
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class ScheduleProvider:
    """
    Data provider responsible for LoanSchedule persistence.

    Responsibilities:

    - Generate repayment schedules
    - Retrieve installments
    - Update installment status
    - Track payment progress

    Does NOT handle:

    - Payment execution
    - Accounting entries
    - Balance calculations
    """

    def __init__(self, session: Session):
        """
        Initialize provider with database session.

        Args:
            session (Session): Active SQLModel session.
        """
        self.session = session

    # ------------------------------------------------------------
    # Schedule generation
    # ------------------------------------------------------------

    def generate_schedule(self, schedule_data: dict) -> dict:
        """
        Generate complete repayment schedule for a loan.

        Calculates installments using amortization formula.
        Creates all installment records in database.

        Args:
            schedule_data (dict): Schedule parameters from schema.

        Returns:
            dict: Complete schedule with installments.

        Raises:
            NotFoundError: If loan does not exist.
        """
        loan_id = require(schedule_data, "loan_id", UUID)
        start_date = require(schedule_data, "start_date", cast_date)
        frequency = require(schedule_data, "frequency", str)
        
        loan = self.session.get(Loan, loan_id)

        if not loan:
            raise NotFoundError("Loan", str(loan_id))

        # Calculate installments
        installments = self._calculate_installments(
            principal=loan.principal_amount,
            annual_rate=loan.interest_rate,
            term_months=loan.term_months,
            start_date=start_date,
            frequency=frequency
        )

        # Save installments to database
        for inst_data in installments:
            installment = LoanSchedule(
                loan_id=loan_id,
                installment_number=inst_data["installment_number"],
                due_date=inst_data["due_date"],
                principal_due=inst_data["principal_due"],
                interest_due=inst_data["interest_due"],
                total_due=inst_data["total_due"],
                status="PENDING"
            )
            self.session.add(installment)

        self.session.commit()

        # Return complete schedule
        return self._build_schedule_response(loan_id)

    # ------------------------------------------------------------
    # Schedule retrieval
    # ------------------------------------------------------------

    def get_schedule(self, loan_id: UUID) -> dict:
        """
        Retrieve complete schedule for a loan.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            dict: Complete schedule with all installments.

        Raises:
            NotFoundError: If schedule does not exist.
        """
        statement = select(LoanSchedule).where(
            LoanSchedule.loan_id == loan_id
        ).order_by(cast(ColumnElement, LoanSchedule.installment_number))

        installments = self.session.exec(statement).all()

        if not installments:
            raise NotFoundError("LoanSchedule", str(loan_id))

        return self._build_schedule_response(loan_id)

    # ------------------------------------------------------------
    # Single installment
    # ------------------------------------------------------------

    def get_installment(self, installment_id: UUID) -> LoanSchedule:
        """
        Retrieve a single installment by ID.

        Args:
            installment_id (UUID): Installment identifier.

        Returns:
            LoanSchedule

        Raises:
            NotFoundError: If installment does not exist.
        """
        installment = self.session.get(LoanSchedule, installment_id)

        if not installment:
            raise NotFoundError("LoanSchedule", str(installment_id))

        return installment

    def get_next_due_installment(self, loan_id: UUID) -> Optional[LoanSchedule]:
        """
        Get next unpaid installment for a loan.

        Returns None if all installments are paid.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            LoanSchedule | None
        """
        statement = select(LoanSchedule).where(
            LoanSchedule.loan_id == loan_id,
            LoanSchedule.status == "PENDING"
        ).order_by(cast(ColumnElement, LoanSchedule.installment_number))

        return self.session.exec(statement).first()

    # ------------------------------------------------------------
    # Installment status update
    # ------------------------------------------------------------

    def update_installment_status(
        self,
        installment_id: UUID,
        status: str,
        paid_amount: Optional[float] = None
    ) -> LoanSchedule:
        """
        Update installment status after payment application.

        Args:
            installment_id (UUID): Installment identifier.
            status (str): New status (PAID, PARTIALLY_PAID, OVERDUE).
            paid_amount (float, optional): Amount paid toward installment.

        Returns:
            Updated LoanSchedule

        Raises:
            NotFoundError: If installment does not exist.
        """
        installment = self.get_installment(installment_id)

        installment.status = status

        if status == "PAID":
            installment.paid_date = date.today()

        self.session.add(installment)
        self.session.commit()
        self.session.refresh(installment)

        return installment

    # ------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------

    def _calculate_installments(
        self,
        principal: float,
        annual_rate: float,
        term_months: int,
        start_date: date,
        frequency: str
    ) -> List[dict]:
        """
        Calculate installment breakdown using amortization formula.

        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]

        Args:
            principal (float): Loan principal.
            annual_rate (float): Annual interest rate (%).
            term_months (int): Loan term in months.
            start_date (date): First payment date.
            frequency (str): Payment frequency.

        Returns:
            List[dict]: Installment data.
        """
        monthly_rate = (annual_rate / 100) / 12

        # Calculate monthly payment
        if monthly_rate == 0:
            monthly_payment = principal / term_months
        else:
            numerator = monthly_rate * ((1 + monthly_rate) ** term_months)
            denominator = ((1 + monthly_rate) ** term_months) - 1
            monthly_payment = principal * (numerator / denominator)

        installments = []
        remaining_principal = principal
        current_date = start_date

        for i in range(1, term_months + 1):
            interest_due = remaining_principal * monthly_rate
            principal_due = monthly_payment - interest_due

            installments.append({
                "installment_number": i,
                "due_date": current_date,
                "principal_due": round(principal_due, 2),
                "interest_due": round(interest_due, 2),
                "total_due": round(monthly_payment, 2)
            })

            remaining_principal -= principal_due
            current_date = current_date + relativedelta(months=1)

        return installments

    def _build_schedule_response(self, loan_id: UUID) -> dict:
        """
        Build complete schedule response with aggregated totals.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            dict: Schedule with installments and totals.
        """
        statement = select(LoanSchedule).where(
            LoanSchedule.loan_id == loan_id
        ).order_by(cast(ColumnElement, LoanSchedule.installment_number))

        installments = list(self.session.exec(statement).all())

        total_principal = sum(inst.principal_due for inst in installments)
        total_interest = sum(inst.interest_due for inst in installments)

        return {
            "loan_id": loan_id,
            "total_installments": len(installments),
            "total_principal": total_principal,
            "total_interest": total_interest,
            "total_amount": total_principal + total_interest,
            "installments": installments
        }