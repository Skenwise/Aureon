# Middleware/DataProvider/LoanProvider/disbursementProvider.py
"""
Disbursement Data Provider.

Handles persistence and retrieval of LoanDisbursement records.

This provider manages disbursement state only.
It does NOT execute fund transfers.
Execution coordination happens at the service/adapter layer.
"""

from typing import List
from uuid import UUID
from datetime import date
from sqlmodel import Session, select

from database.model.finance.loan_disbursement import LoanDisbursement
from database.model.finance.loan import Loan
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class DisbursementProvider:
    """
    Data provider responsible for LoanDisbursement persistence.

    Responsibilities:

    - Create disbursement records
    - Retrieve disbursement details
    - Update disbursement status
    - Track execution state

    Does NOT handle:

    - Treasury liquidity checks
    - Payment execution
    - Accounting journal creation
    - Loan status updates

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
    # Disbursement creation
    # ------------------------------------------------------------

    def create_disbursement(self, disbursement_data: dict) -> LoanDisbursement:
        """
        Create a disbursement record for a loan.

        Validates loan is in correct state (PENDING).

        Args:
            disbursement_data (dict): Disbursement data from schema.

        Returns:
            LoanDisbursement

        Raises:
            NotFoundError: If loan does not exist.
            ValidationError: If loan status is invalid for disbursement.
        """
        loan_id = require(disbursement_data, "loan_id", UUID)
        disbursement_amount = require(disbursement_data, "disbursement_amount", float)
        disbursement_account_id = require(disbursement_data, "disbursement_account_id", UUID)
        disbursement_date = require(disbursement_data, "disbursement_date", cast_date)
        payment_provider = require(disbursement_data, "payment_provider", str)
        
        loan = self.session.get(Loan, loan_id)

        if not loan:
            raise NotFoundError("Loan", str(loan_id))

        if loan.status not in ["PENDING", "DISBURSED"]:
            raise ValidationError(
                f"Cannot disburse loan with status {loan.status}"
            )

        disbursement = LoanDisbursement(
            loan_id=loan_id,
            disbursement_amount=disbursement_amount,
            disbursement_account_id=disbursement_account_id,
            disbursement_date=disbursement_date,
            payment_provider=payment_provider,
            status="PENDING",
            reference=disbursement_data.get("reference"),
            notes=disbursement_data.get("notes")
        )

        self.session.add(disbursement)
        self.session.commit()
        self.session.refresh(disbursement)

        return disbursement

    # ------------------------------------------------------------
    # Disbursement retrieval
    # ------------------------------------------------------------

    def get_disbursement(self, disbursement_id: UUID) -> LoanDisbursement:
        """
        Retrieve disbursement by ID.

        Args:
            disbursement_id (UUID): Disbursement identifier.

        Returns:
            LoanDisbursement

        Raises:
            NotFoundError: If disbursement does not exist.
        """
        disbursement = self.session.get(LoanDisbursement, disbursement_id)

        if not disbursement:
            raise NotFoundError("LoanDisbursement", str(disbursement_id))

        return disbursement

    def list_disbursements(self, loan_id: UUID) -> List[LoanDisbursement]:
        """
        List all disbursements for a specific loan.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            List[LoanDisbursement]
        """
        statement = select(LoanDisbursement).where(
            LoanDisbursement.loan_id == loan_id
        )

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Disbursement execution
    # ------------------------------------------------------------

    def execute_disbursement(self, disbursement_id: UUID) -> LoanDisbursement:
        """
        Execute a disbursement.

        NOTE:
        This method only updates disbursement status.
        Actual coordination with treasury/payments/accounting
        happens at the adapter/service layer.

        Workflow (handled externally):
        1. Check treasury liquidity
        2. Execute payment
        3. Create accounting journal
        4. Update loan status to DISBURSED → ACTIVE
        5. Call this method to mark COMPLETED

        Args:
            disbursement_id (UUID): Disbursement identifier.

        Returns:
            Updated LoanDisbursement

        Raises:
            NotFoundError: If disbursement does not exist.
            ValidationError: If disbursement already executed.
        """
        disbursement = self.get_disbursement(disbursement_id)

        if disbursement.status != "PENDING":
            raise ValidationError(
                f"Disbursement already {disbursement.status}"
            )

        disbursement.status = "COMPLETED"

        self.session.add(disbursement)
        self.session.commit()
        self.session.refresh(disbursement)

        return disbursement

    def fail_disbursement(
        self,
        disbursement_id: UUID,
        reason: str
    ) -> LoanDisbursement:
        """
        Mark disbursement as failed.

        Args:
            disbursement_id (UUID): Disbursement identifier.
            reason (str): Failure reason.

        Returns:
            Updated LoanDisbursement

        Raises:
            NotFoundError: If disbursement does not exist.
        """
        disbursement = self.get_disbursement(disbursement_id)

        disbursement.status = "FAILED"
        disbursement.notes = f"{disbursement.notes or ''}\nFailed: {reason}"

        self.session.add(disbursement)
        self.session.commit()
        self.session.refresh(disbursement)

        return disbursement