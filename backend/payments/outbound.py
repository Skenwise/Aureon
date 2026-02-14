# backend/payments/outbound.py
"""
Outbound Payment Port & Adapter.
Defines outbound payment operations and delegates to OutboundPaymentProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.paymentSchema import OutboundPaymentCreate, OutboundPaymentRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.PaymentProvider.outboundProvider import OutboundPaymentProvider


class OutboundPaymentPort(Protocol):
    """
    Port interface for outbound payment operations.
    All operations handle money leaving the system.
    No provider or infrastructure logic should be handled here.
    """

    def create_outbound_payment(self, payment_in: OutboundPaymentCreate) -> OutboundPaymentRead:
        """
        Create an outbound payment request.
        
        Args:
            payment_in (OutboundPaymentCreate): Input data for payment creation.
        
        Returns:
            OutboundPaymentRead: The created payment record.
        
        Raises:
            ValidationError: If payment data is invalid or insufficient funds.
        """
        raise NotImplementedError

    def get_outbound_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Retrieve an outbound payment by its unique ID.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            OutboundPaymentRead: Payment details.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError

    def get_payment_by_number(self, payment_number: str) -> OutboundPaymentRead:
        """
        Retrieve an outbound payment by its payment number.
        
        Args:
            payment_number (str): Unique payment number.
        
        Returns:
            OutboundPaymentRead: Payment details.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError

    def list_outbound_payments(
        self, 
        source_account_id: UUID | None = None,
        status: str | None = None
    ) -> List[OutboundPaymentRead]:
        """
        List all outbound payments, optionally filtered by source account or status.
        
        Args:
            source_account_id (UUID, optional): Filter by source account.
            status (str, optional): Filter by payment status.
        
        Returns:
            List[OutboundPaymentRead]: All matching payment records.
        """
        raise NotImplementedError

    def execute_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Execute a pending outbound payment.
        Coordinates: Treasury → Provider → Accounting.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            OutboundPaymentRead: Updated payment with execution status.
        
        Raises:
            NotFoundError: If the payment does not exist.
            ValidationError: If payment cannot be executed (insufficient funds, invalid status).
        """
        raise NotImplementedError

    def cancel_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Cancel a pending outbound payment.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            OutboundPaymentRead: Updated payment with CANCELLED status.
        
        Raises:
            NotFoundError: If the payment does not exist.
            ValidationError: If payment cannot be cancelled.
        """
        raise NotImplementedError


class OutboundPaymentAdapter(OutboundPaymentPort):
    """
    Adapter implementation of OutboundPaymentPort.
    Delegates all outbound payment operations to OutboundPaymentProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: OutboundPaymentProvider):
        """
        Initialize the adapter with an outbound payment provider.
        
        Args:
            provider (OutboundPaymentProvider): The data provider for outbound payment operations.
        """
        self.provider = provider

    def create_outbound_payment(self, payment_in: OutboundPaymentCreate) -> OutboundPaymentRead:
        """
        Create outbound payment via provider implementation.
        """
        payment_model = self.provider.create_outbound_payment(cast(Any, payment_in))
        return OutboundPaymentRead.model_validate(payment_model)

    def get_outbound_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Retrieve outbound payment by ID via provider implementation.
        """
        payment_model = self.provider.get_outbound_payment(payment_id)
        return OutboundPaymentRead.model_validate(payment_model)

    def get_payment_by_number(self, payment_number: str) -> OutboundPaymentRead:
        """
        Retrieve outbound payment by payment number via provider implementation.
        """
        payment_model = self.provider.get_payment_by_number(payment_number)
        return OutboundPaymentRead.model_validate(payment_model)

    def list_outbound_payments(
        self, 
        source_account_id: UUID | None = None,
        status: str | None = None
    ) -> List[OutboundPaymentRead]:
        """
        List outbound payments via provider, optionally filtered.
        """
        payments = self.provider.list_outbound_payments(source_account_id, status)
        return [OutboundPaymentRead.model_validate(payment) for payment in payments]

    def execute_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Execute payment via provider implementation.
        Provider coordinates with treasury, execution providers, and accounting.
        """
        payment_model = self.provider.execute_payment(payment_id)
        return OutboundPaymentRead.model_validate(payment_model)

    def cancel_payment(self, payment_id: UUID) -> OutboundPaymentRead:
        """
        Cancel payment via provider implementation.
        """
        payment_model = self.provider.cancel_payment(payment_id)
        return OutboundPaymentRead.model_validate(payment_model)