# Middleware/DataProvider/LoanProvider/repaymentProvider.py
"""
Repayment Data Provider.

Handles persistence and retrieval of LoanRepayment records.

This provider manages repayment state only.
It does NOT process payments or update accounting.
Execution coordination happens at the service/adapter layer.
"""

from typing import List
from uuid import UUID
from datetime import date
from sqlmodel import Session, select

from database.model.finance.loan_repayment import LoanRepayment
from database.model.finance.loan import Loan
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class RepaymentProvider:
    """
    Data provider responsible for LoanRepayment persistence.

    Responsibilities:

    - Create repayment records
    - Retrieve repayment details
    - Update repayment status
    - Track payment application

    Does NOT handle:

    - Payment receipt processing
    - Payment allocation logic
    - Schedule installment updates
    - Accounting journal creation

    Orchestration happens at adapter/service layer.
    """

    def __init__(self, session: Session):
        """
        Initialize provider with database session.

        Args:
            session (Session): Active SQLModel session.
        """
        self.session = session

    # ------------------------------------------------------------
    # Repayment creation
    # ------------------------------------------------------------

    def create_repayment(self, repayment_data: dict) -> LoanRepayment:
        """
        Create a repayment record for a loan.

        Validates loan is in ACTIVE state.

        Args:
            repayment_data (dict): Repayment data from schema.

        Returns:
            LoanRepayment

        Raises:
            NotFoundError: If loan does not exist.
            ValidationError: If loan status is not ACTIVE.
        """
        loan_id = require(repayment_data, "loan_id", UUID)
        payment_amount = require(repayment_data, "payment_amount", float)
        payment_date = require(repayment_data, "payment_date", cast_date)
        payment_method = require(repayment_data, "payment_method", str)
        
        loan = self.session.get(Loan, loan_id)

        if not loan:
            raise NotFoundError("Loan", str(loan_id))

        if loan.status != "ACTIVE":
            raise ValidationError(
                f"Cannot accept payment for loan with status {loan.status}"
            )

        # Payment allocation will be calculated in apply_repayment
        repayment = LoanRepayment(
            loan_id=loan_id,
            payment_amount=payment_amount,
            principal_applied=0.0,  # Calculated on apply
            interest_applied=0.0,   # Calculated on apply
            payment_date=payment_date,
            payment_method=payment_method,
            payment_provider=repayment_data.get("payment_provider"),
            status="PENDING",
            reference=repayment_data.get("reference"),
            notes=repayment_data.get("notes")
        )

        self.session.add(repayment)
        self.session.commit()
        self.session.refresh(repayment)

        return repayment

    # ------------------------------------------------------------
    # Repayment retrieval
    # ------------------------------------------------------------

    def get_repayment(self, repayment_id: UUID) -> LoanRepayment:
        """
        Retrieve repayment by ID.

        Args:
            repayment_id (UUID): Repayment identifier.

        Returns:
            LoanRepayment

        Raises:
            NotFoundError: If repayment does not exist.
        """
        repayment = self.session.get(LoanRepayment, repayment_id)

        if not repayment:
            raise NotFoundError("LoanRepayment", str(repayment_id))

        return repayment

    def list_repayments(self, loan_id: UUID) -> List[LoanRepayment]:
        """
        List all repayments for a specific loan.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            List[LoanRepayment]
        """
        statement = select(LoanRepayment).where(
            LoanRepayment.loan_id == loan_id
        )

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Repayment application
    # ------------------------------------------------------------

    def apply_repayment(self, repayment_id: UUID) -> LoanRepayment:
        """
        Apply a repayment to the loan.

        NOTE:
        This method only updates repayment status.
        Actual coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Get next due installment(s)
        2. Allocate payment (interest first, then principal)
        3. Update schedule installment status
        4. Create accounting journal entry
        5. Update loan balance
        6. Call this method to mark APPLIED

        Args:
            repayment_id (UUID): Repayment identifier.

        Returns:
            Updated LoanRepayment

        Raises:
            NotFoundError: If repayment does not exist.
            ValidationError: If repayment already applied.
        """
        repayment = self.get_repayment(repayment_id)

        if repayment.status != "PENDING":
            raise ValidationError(
                f"Repayment already {repayment.status}"
            )

        # NOTE: Allocation logic handled externally
        # For now, simplified allocation
        payment_amount = repayment.payment_amount
        interest_applied = payment_amount * 0.2  # Placeholder
        principal_applied = payment_amount - interest_applied

        repayment.interest_applied = interest_applied
        repayment.principal_applied = principal_applied
        repayment.status = "APPLIED"

        self.session.add(repayment)
        self.session.commit()
        self.session.refresh(repayment)

        return repayment

    def reverse_repayment(
        self,
        repayment_id: UUID,
        reason: str
    ) -> LoanRepayment:
        """
        Reverse a previously applied repayment.

        NOTE:
        This method only updates repayment status.
        Actual reversal coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Reverse accounting journal entry
        2. Revert schedule installment updates
        3. Restore loan balance
        4. Call this method to mark REVERSED

        Args:
            repayment_id (UUID): Repayment identifier.
            reason (str): Reversal reason.

        Returns:
            Updated LoanRepayment

        Raises:
            NotFoundError: If repayment does not exist.
            ValidationError: If repayment cannot be reversed.
        """
        repayment = self.get_repayment(repayment_id)

        if repayment.status != "APPLIED":
            raise ValidationError(
                "Can only reverse APPLIED repayments"
            )

        repayment.status = "REVERSED"
        repayment.notes = f"{repayment.notes or ''}\nReversed: {reason}"

        self.session.add(repayment)
        self.session.commit()
        self.session.refresh(repayment)

        return repayment