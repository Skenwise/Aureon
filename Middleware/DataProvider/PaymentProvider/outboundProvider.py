# Middleware/DataProvider/PaymentProvider/outboundProvider.py
"""
Outbound Payment Data Provider.

Handles persistence and retrieval of outbound Payment records.

This provider manages outbound payment state only.
It does NOT execute fund transfers or make API calls.
Execution coordination happens at the adapter/service layer.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select

from database.model.payments.payment import Payment
from database.model.payments.payment_execution import PaymentExecution
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class OutboundPaymentProvider:
    """
    Data provider responsible for outbound Payment persistence.

    Responsibilities:

    - Create outbound payment records
    - Retrieve payment details
    - Update payment status
    - Track execution attempts

    Does NOT handle:

    - Treasury liquidity checks
    - Provider execution (API calls)
    - Accounting journal creation
    - Fund transfers

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
    # Outbound payment creation
    # ------------------------------------------------------------

    def create_outbound_payment(self, payment_data: dict) -> Payment:
        """
        Create an outbound payment record.

        Args:
            payment_data (dict): Payment data from schema.

        Returns:
            Payment

        Raises:
            ValidationError: If payment data is invalid.
        """
        # Generate unique payment number
        payment_number = self._generate_payment_number()

        # Extract and validate required fields
        amount = require(payment_data, "amount", float)
        currency_code = require(payment_data, "currency_code", str)
        source_account_id = require(payment_data, "source_account_id", UUID)
        provider_type = require(payment_data, "provider_type", str)

        payment = Payment(
            payment_number=payment_number,
            payment_type="OUTBOUND",
            direction="OUT",
            amount=amount,
            currency=currency_code,
            status="PENDING",
            source_account_id=source_account_id,
            destination_account_id=payment_data.get("destination_account_id"),
            provider_type=provider_type,
            provider_id=payment_data.get("provider_id"),
            reference=payment_data.get("reference"),
            notes=payment_data.get("notes")
        )

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Payment retrieval
    # ------------------------------------------------------------

    def get_outbound_payment(self, payment_id: UUID) -> Payment:
        """
        Retrieve outbound payment by ID.

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.session.get(Payment, payment_id)

        if not payment or payment.payment_type != "OUTBOUND":
            raise NotFoundError("OutboundPayment", str(payment_id))

        return payment

    def get_payment_by_number(self, payment_number: str) -> Payment:
        """
        Retrieve outbound payment by payment number.

        Args:
            payment_number (str): Unique payment number.

        Returns:
            Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        statement = select(Payment).where(
            Payment.payment_number == payment_number,
            Payment.payment_type == "OUTBOUND"
        )
        payment = self.session.exec(statement).first()

        if not payment:
            raise NotFoundError("OutboundPayment", payment_number)

        return payment

    # ------------------------------------------------------------
    # List outbound payments
    # ------------------------------------------------------------

    def list_outbound_payments(
        self,
        source_account_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Payment]:
        """
        List outbound payments with optional filters.

        Args:
            source_account_id (UUID, optional): Filter by source account.
            status (str, optional): Filter by payment status.

        Returns:
            List[Payment]
        """
        statement = select(Payment).where(Payment.payment_type == "OUTBOUND")

        if source_account_id:
            statement = statement.where(Payment.source_account_id == source_account_id)

        if status:
            statement = statement.where(Payment.status == status)

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Payment execution
    # ------------------------------------------------------------

    def execute_payment(self, payment_id: UUID) -> Payment:
        """
        Execute an outbound payment.

        NOTE:
        This method only updates payment status.
        Actual coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Check treasury liquidity
        2. Reserve funds
        3. Execute via payment provider
        4. Create accounting journal
        5. Call this method to mark COMPLETED

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
            ValidationError: If payment cannot be executed.
        """
        payment = self.get_outbound_payment(payment_id)

        if payment.status != "PENDING":
            raise ValidationError(
                f"Payment already {payment.status}"
            )

        payment.status = "PROCESSING"
        payment.processed_at = datetime.now(timezone.utc)

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    def complete_payment(self, payment_id: UUID, provider_reference: str) -> Payment:
        """
        Mark payment as completed after successful execution.

        Args:
            payment_id (UUID): Payment identifier.
            provider_reference (str): External provider reference.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.get_outbound_payment(payment_id)

        payment.status = "COMPLETED"
        payment.provider_reference = provider_reference

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    def fail_payment(self, payment_id: UUID, error_message: str) -> Payment:
        """
        Mark payment as failed.

        Args:
            payment_id (UUID): Payment identifier.
            error_message (str): Error message.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.get_outbound_payment(payment_id)

        payment.status = "FAILED"
        payment.notes = f"{payment.notes or ''}\nFailed: {error_message}"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Payment cancellation
    # ------------------------------------------------------------

    def cancel_payment(self, payment_id: UUID) -> Payment:
        """
        Cancel a pending payment.

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
            ValidationError: If payment cannot be cancelled.
        """
        payment = self.get_outbound_payment(payment_id)

        if payment.status not in ["PENDING", "PROCESSING"]:
            raise ValidationError(
                f"Cannot cancel payment with status {payment.status}"
            )

        payment.status = "CANCELLED"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Execution tracking
    # ------------------------------------------------------------

    def create_execution_attempt(
        self,
        payment_id: UUID,
        provider_id: Optional[UUID] = None,
        attempt_number: int = 1
    ) -> PaymentExecution:
        """
        Create execution attempt record.

        Args:
            payment_id (UUID): Payment identifier.
            provider_id (UUID, optional): Provider ID.
            attempt_number (int): Attempt number.

        Returns:
            PaymentExecution
        """
        execution = PaymentExecution(
            payment_id=payment_id,
            provider_id=provider_id,
            attempt_number=attempt_number,
            status="INITIATED"
        )

        self.session.add(execution)
        self.session.commit()
        self.session.refresh(execution)

        return execution

    # ------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------

    def _generate_payment_number(self) -> str:
        """
        Generate unique payment number.

        Format: OUT-{timestamp}-{random}

        Returns:
            str: Unique payment number.
        """
        import random
        import string

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = "".join(random.choices(string.digits, k=4))

        return f"OUT-{timestamp}-{random_suffix}"