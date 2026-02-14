# Middleware/DataProvider/PaymentProvider/inboundProvider.py
"""
Inbound Payment Data Provider.

Handles persistence and retrieval of inbound Payment records.

This provider manages inbound payment state only.
It does NOT verify payments with external providers.
Verification coordination happens at the adapter/service layer.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select

from database.model.payments.payment import Payment
from database.model.payments.payment_execution import PaymentExecution
from backend.core.error import NotFoundError, ValidationError
from backend.core.utils import require, cast_date


class InboundPaymentProvider:
    """
    Data provider responsible for inbound Payment persistence.

    Responsibilities:

    - Create inbound payment records
    - Retrieve payment details
    - Update payment status
    - Track verification attempts

    Does NOT handle:

    - Provider verification (API calls)
    - Treasury balance updates
    - Accounting journal creation
    - Webhook signature validation

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
    # Inbound payment creation
    # ------------------------------------------------------------

    def create_inbound_payment(self, payment_data: dict) -> Payment:
        """
        Create an inbound payment record.

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
        destination_account_id = require(payment_data, "destination_account_id", UUID)
        provider_type = require(payment_data, "provider_type", str)

        payment = Payment(
            payment_number=payment_number,
            payment_type="INBOUND",
            direction="IN",
            amount=amount,
            currency=currency_code,
            status="PENDING",
            destination_account_id=destination_account_id,
            provider_type=provider_type,
            provider_id=payment_data.get("provider_id"),
            provider_reference=payment_data.get("provider_reference"),
            external_transaction_id=payment_data.get("external_transaction_id"),
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

    def get_inbound_payment(self, payment_id: UUID) -> Payment:
        """
        Retrieve inbound payment by ID.

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.session.get(Payment, payment_id)

        if not payment or payment.payment_type != "INBOUND":
            raise NotFoundError("InboundPayment", str(payment_id))

        return payment

    def get_payment_by_number(self, payment_number: str) -> Payment:
        """
        Retrieve inbound payment by payment number.

        Args:
            payment_number (str): Unique payment number.

        Returns:
            Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        statement = select(Payment).where(
            Payment.payment_number == payment_number,
            Payment.payment_type == "INBOUND"
        )
        payment = self.session.exec(statement).first()

        if not payment:
            raise NotFoundError("InboundPayment", payment_number)

        return payment

    def get_payment_by_provider_reference(self, provider_reference: str) -> Payment:
        """
        Retrieve inbound payment by provider reference.

        Args:
            provider_reference (str): External provider reference.

        Returns:
            Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        statement = select(Payment).where(
            Payment.provider_reference == provider_reference,
            Payment.payment_type == "INBOUND"
        )
        payment = self.session.exec(statement).first()

        if not payment:
            raise NotFoundError("InboundPayment", provider_reference)

        return payment

    # ------------------------------------------------------------
    # List inbound payments
    # ------------------------------------------------------------

    def list_inbound_payments(
        self,
        destination_account_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Payment]:
        """
        List inbound payments with optional filters.

        Args:
            destination_account_id (UUID, optional): Filter by destination account.
            status (str, optional): Filter by payment status.

        Returns:
            List[Payment]
        """
        statement = select(Payment).where(Payment.payment_type == "INBOUND")

        if destination_account_id:
            statement = statement.where(Payment.destination_account_id == destination_account_id)

        if status:
            statement = statement.where(Payment.status == status)

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Payment processing
    # ------------------------------------------------------------

    def process_payment(self, payment_id: UUID) -> Payment:
        """
        Process an inbound payment.

        NOTE:
        This method only updates payment status.
        Actual coordination happens at adapter/service layer.

        Workflow (handled externally):
        1. Verify with payment provider
        2. Update treasury balance
        3. Create accounting journal
        4. Call this method to mark COMPLETED

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
            ValidationError: If payment cannot be processed.
        """
        payment = self.get_inbound_payment(payment_id)

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

    def complete_payment(self, payment_id: UUID) -> Payment:
        """
        Mark payment as completed after successful processing.

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.get_inbound_payment(payment_id)

        payment.status = "COMPLETED"

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
        payment = self.get_inbound_payment(payment_id)

        payment.status = "FAILED"
        payment.notes = f"{payment.notes or ''}\nFailed: {error_message}"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Payment verification
    # ------------------------------------------------------------

    def verify_payment(self, payment_id: UUID) -> Payment:
        """
        Mark payment as verified.

        Args:
            payment_id (UUID): Payment identifier.

        Returns:
            Updated Payment

        Raises:
            NotFoundError: If payment does not exist.
        """
        payment = self.get_inbound_payment(payment_id)

        payment.status = "VERIFIED"

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return payment

    # ------------------------------------------------------------
    # Execution tracking
    # ------------------------------------------------------------

    def create_verification_attempt(
        self,
        payment_id: UUID,
        provider_id: Optional[UUID] = None,
        attempt_number: int = 1
    ) -> PaymentExecution:
        """
        Create verification attempt record.

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

        Format: IN-{timestamp}-{random}

        Returns:
            str: Unique payment number.
        """
        import random
        import string

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = "".join(random.choices(string.digits, k=4))

        return f"IN-{timestamp}-{random_suffix}"