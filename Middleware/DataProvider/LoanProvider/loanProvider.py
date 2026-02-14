# Middleware/DataProvider/LoanProvider/loanProvider.py
"""
Loan Data Provider.

Handles persistence and retrieval of Loan records.

This provider is the authoritative storage layer for loan contracts.
It does NOT execute disbursements or repayments.
It only manages the state of Loan contracts.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select

from database.model.finance.loan import Loan
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class LoanProvider:
    """
    Data provider responsible for Loan persistence.

    Responsibilities:

    - Create loan contracts
    - Retrieve loan records
    - Update loan status (state machine)
    - List loans with filters

    Does NOT handle:

    - Disbursement execution
    - Repayment processing
    - Accounting journal creation
    """

    def __init__(self, session: Session):
        """
        Initialize provider with database session.

        Args:
            session (Session): Active SQLModel session.
        """
        self.session = session

    # ------------------------------------------------------------
    # Loan creation
    # ------------------------------------------------------------

    def create_loan(self, loan_data: dict) -> Loan:
        """
        Create a new loan contract.

        Args:
            loan_data (dict): Loan creation data from schema.

        Returns:
            Loan

        Raises:
            ValidationError: If borrower does not exist or data is invalid.
        """
        # Generate unique loan number
        loan_number = self._generate_loan_number()

        # Extract and validate required fields
        borrower_id = require(loan_data, "borrower_id", UUID)
        principal_amount = require(loan_data, "principal_amount", float)
        interest_rate = require(loan_data, "interest_rate", float)
        start_date = require(loan_data, "start_date", cast_date)
        term_months = require(loan_data, "term_months", int)
        currency_code = require(loan_data, "currency_code", str)

        # Calculate maturity date
        from dateutil.relativedelta import relativedelta
        maturity_date = start_date + relativedelta(months=term_months)

        loan = Loan(
            customer_id=borrower_id,
            loan_number=loan_number,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            start_date=start_date,
            end_date=maturity_date,
            term_months=term_months,
            status="PENDING",
            currency=currency_code,
            metadata_=loan_data.get("notes")
        )

        self.session.add(loan)
        self.session.commit()
        self.session.refresh(loan)

        return loan

    # ------------------------------------------------------------
    # Loan retrieval
    # ------------------------------------------------------------

    def get_loan(self, loan_id: UUID) -> Loan:
        """
        Retrieve loan by ID.

        Args:
            loan_id (UUID): Loan identifier.

        Returns:
            Loan

        Raises:
            NotFoundError: If loan does not exist.
        """
        loan = self.session.get(Loan, loan_id)

        if not loan:
            raise NotFoundError("Loan", str(loan_id))

        return loan

    def get_loan_by_number(self, loan_number: str) -> Loan:
        """
        Retrieve loan by loan number.

        Args:
            loan_number (str): Unique loan number.

        Returns:
            Loan

        Raises:
            NotFoundError: If loan does not exist.
        """
        statement = select(Loan).where(Loan.loan_number == loan_number)
        loan = self.session.exec(statement).first()

        if not loan:
            raise NotFoundError("Loan", loan_number)

        return loan

    # ------------------------------------------------------------
    # List loans
    # ------------------------------------------------------------

    def list_loans(
        self,
        borrower_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Loan]:
        """
        List all loans with optional filters.

        Args:
            borrower_id (UUID, optional): Filter by borrower.
            status (str, optional): Filter by loan status.

        Returns:
            List[Loan]
        """
        statement = select(Loan)

        if borrower_id:
            statement = statement.where(Loan.customer_id == borrower_id)

        if status:
            statement = statement.where(Loan.status == status)

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Status update (state machine)
    # ------------------------------------------------------------

    def update_loan_status(self, loan_id: UUID, status: str) -> Loan:
        """
        Update loan status following state machine rules.

        Valid transitions:
        PENDING → DISBURSED
        DISBURSED → ACTIVE
        ACTIVE → CLOSED | DEFAULTED

        Args:
            loan_id (UUID): Loan identifier.
            status (str): New status.

        Returns:
            Updated Loan

        Raises:
            NotFoundError: If loan does not exist.
            ValidationError: If status transition is invalid.
        """
        loan = self.get_loan(loan_id)
        if loan.status is None:
            raise ValidationError("Current loan status is undefined")

        # Define valid state transitions
        valid_transitions = {
            "PENDING": ["DISBURSED"],
            "DISBURSED": ["ACTIVE"],
            "ACTIVE": ["CLOSED", "DEFAULTED"],
            "CLOSED": [],
            "DEFAULTED": []
        }

        allowed_statuses = valid_transitions.get(loan.status, [])

        if status not in allowed_statuses:
            raise ValidationError(
                f"Invalid status transition from {loan.status} to {status}"
            )

        loan.status = status
        self.session.add(loan)
        self.session.commit()
        self.session.refresh(loan)

        return loan

    # ------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------

    def _generate_loan_number(self) -> str:
        """
        Generate unique loan number.

        Format: LN-{timestamp}-{random}

        Returns:
            str: Unique loan number.
        """
        import random
        import string

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = "".join(random.choices(string.digits, k=4))

        return f"LN-{timestamp}-{random_suffix}"