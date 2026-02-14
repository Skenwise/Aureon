# Middleware/DataProvider/PaymentProvider/settlementProvider.py
"""
Settlement Data Provider.

Handles persistence and retrieval of internal Settlement records.

This provider manages settlement state only.
It does NOT execute internal transfers.
Execution coordination happens at the adapter/service layer.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select

from database.model.payments.payment import Payment
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class SettlementProvider:
    """
    Data provider responsible for Settlement persistence.

    Responsibilities:

    - Create settlement records
    - Retrieve settlement details
    - Update settlement status
    - Track settlement history

    Does NOT handle:

    - Internal provider execution
    - Accounting journal creation
    - Balance updates

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
    # Settlement creation
    # ------------------------------------------------------------

    def create_settlement(self, settlement_data: dict) -> Payment:
        """
        Create an internal settlement record.

        Args:
            settlement_data (dict): Settlement data from schema.

        Returns:
            Payment

        Raises:
            ValidationError: If settlement data is invalid.
        """
        # Generate unique payment number
        payment_number = self._generate_payment_number()

        # Extract and validate required fields
        amount = require(settlement_data, "amount", float)
        currency_code = require(settlement_data, "currency_code", str)
        source_account_id = require(settlement_data, "source_account_id", UUID)
        destination_account_id = require(settlement_data, "destination_account_id", UUID)
        settlement_type = require(settlement_data, "settlement_type", str)

        # Validate source != destination
        if source_account_id == destination_account_id:
            raise ValidationError(
                "Source and destination accounts cannot be the same"
            )

        payment = Payment(
            payment_number=payment_number,
            payment_type="SETTLEMENT",
            direction="INTERNAL",
            amount=amount,
            currency=currency_code,
            status="PENDING",
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            provider_type="INTERNAL",
            reference=settlement_data.get("reference"),
            notes=settlement_data.get("notes"),
            metadata_=f'{{"settlement_type": "{settlement_type}"}}'
        )

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Settlement retrieval
    # ------------------------------------------------------------

    def get_settlement(self, settlement_id: UUID) -> Payment:
        """
        Retrieve settlement by ID.

        Args:
            settlement_id (UUID): Settlement identifier.

        Returns:
            Payment

        Raises:
            NotFoundError: If settlement does not exist.
        """
        payment = self.session.get(Payment, settlement_id)

        if not payment or payment.payment_type != "SETTLEMENT":
            raise NotFoundError("Settlement", str(settlement_id))

        return payment

    def get_settlement_by_number(self, payment_number: str) -> Payment:
        """
        Retrieve settlement by payment number.

        Args:
            payment_number (str): Unique payment number.

        Returns:
            Payment

        Raises:
            NotFoundError: If settlement does not exist.
        """
        statement = select(Payment).where(
            Payment.payment_number == payment_number,
            Payment.payment_type == "SETTLEMENT"
        )
        payment = self.session.exec(statement).first()

        if not payment:
            raise NotFoundError("Settlement", payment_number)

        return payment

    # ------------------------------------------------------------
    # List settlements
    # ------------------------------------------------------------

    def list_settlements(
        self,
        account_id: Optional[UUID] = None,
        settlement_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Payment]:
        """
        List settlements with optional filters.

        Args:
            account_id (UUID, optional): Filter by source or destination account.
            settlement_type (str, optional): Filter by settlement type.
            status (str, optional): Filter by settlement status.

        Returns:
            List[Payment]
        """
        statement = select(Payment).where(Payment.payment_type == "SETTLEMENT")

        if account_id:
            statement = statement.where(
                (Payment.source_account_id == account_id) |
                (Payment.destination_account_id == account_id)
            )

        if status:
            statement = statement.where(Payment.status == status)

        # Note: settlement_type filtering would require JSON parsing of metadata_
        # Implement if needed

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Settlement execution
    # ------------------------------------------------------------

    def execute_settlement(self, settlement_id: UUID) -> Payment:
        """
        Execute an internal settlement.

        NOTE:
        This method only updates settlement status.
        Actual coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Execute via internal provider (no network)
        2. Create accounting journal
        3. Call this method to mark COMPLETED

        Args:
            settlement_id (UUID): Settlement identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If settlement does not exist.
            ValidationError: If settlement cannot be executed.
        """
        payment = self.get_settlement(settlement_id)

        if payment.status != "PENDING":
            raise ValidationError(
                f"Settlement already {payment.status}"
            )

        payment.status = "PROCESSING"
        payment.processed_at = datetime.now(timezone.utc)

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    def complete_settlement(self, settlement_id: UUID) -> Payment:
        """
        Mark settlement as completed.

        Args:
            settlement_id (UUID): Settlement identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If settlement does not exist.
        """
        payment = self.get_settlement(settlement_id)

        payment.status = "COMPLETED"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    def fail_settlement(self, settlement_id: UUID, error_message: str) -> Payment:
        """
        Mark settlement as failed.

        Args:
            settlement_id (UUID): Settlement identifier.
            error_message (str): Error message.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If settlement does not exist.
        """
        payment = self.get_settlement(settlement_id)

        payment.status = "FAILED"
        payment.notes = f"{payment.notes or ''}\nFailed: {error_message}"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Settlement reversal
    # ------------------------------------------------------------

    def reverse_settlement(self, settlement_id: UUID, reason: str) -> Payment:
        """
        Reverse a completed settlement.

        NOTE:
        This method only updates settlement status.
        Actual reversal coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Reverse accounting journal
        2. Create reverse settlement
        3. Call this method to mark REVERSED

        Args:
            settlement_id (UUID): Settlement identifier.
            reason (str): Reversal reason.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If settlement does not exist.
            ValidationError: If settlement cannot be reversed.
        """
        payment = self.get_settlement(settlement_id)

        if payment.status != "COMPLETED":
            raise ValidationError(
                "Can only reverse COMPLETED settlements"
            )

        payment.status = "REVERSED"
        payment.notes = f"{payment.notes or ''}\nReversed: {reason}"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------

    def _generate_payment_number(self) -> str:
        """
        Generate unique payment number.

        Format: STL-{timestamp}-{random}

        Returns:
            str: Unique payment number.
        """
        import random
        import string

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = "".join(random.choices(string.digits, k=4))

        return f"STL-{timestamp}-{random_suffix}"