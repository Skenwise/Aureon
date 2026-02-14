# backend/payments/inbound.py
"""
Inbound Payment Port & Adapter.
Defines inbound payment operations and delegates to InboundPaymentProvider.
"""
from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.paymentSchema import InboundPaymentCreate, InboundPaymentRead
from backend.core.error import NotFoundError, ValidationError
from Middleware.DataProvider.PaymentProvider.inboundProvider import InboundPaymentProvider


class InboundPaymentPort(Protocol):
    """
    Port interface for inbound payment operations.
    All operations handle money entering the system.
    No provider or infrastructure logic should be handled here.
    """

    def create_inbound_payment(self, payment_in: InboundPaymentCreate) -> InboundPaymentRead:
        """
        Create an inbound payment record.
        
        Args:
            payment_in (InboundPaymentCreate): Input data for payment creation.
        
        Returns:
            InboundPaymentRead: The created payment record.
        
        Raises:
            ValidationError: If payment data is invalid.
        """
        raise NotImplementedError

    def get_inbound_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Retrieve an inbound payment by its unique ID.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            InboundPaymentRead: Payment details.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError

    def get_payment_by_number(self, payment_number: str) -> InboundPaymentRead:
        """
        Retrieve an inbound payment by its payment number.
        
        Args:
            payment_number (str): Unique payment number.
        
        Returns:
            InboundPaymentRead: Payment details.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError

    def get_payment_by_provider_reference(self, provider_reference: str) -> InboundPaymentRead:
        """
        Retrieve an inbound payment by provider reference.
        Used for webhook verification.
        
        Args:
            provider_reference (str): External provider reference.
        
        Returns:
            InboundPaymentRead: Payment details.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError

    def list_inbound_payments(
        self, 
        destination_account_id: UUID | None = None,
        status: str | None = None
    ) -> List[InboundPaymentRead]:
        """
        List all inbound payments, optionally filtered by destination account or status.
        
        Args:
            destination_account_id (UUID, optional): Filter by destination account.
            status (str, optional): Filter by payment status.
        
        Returns:
            List[InboundPaymentRead]: All matching payment records.
        """
        raise NotImplementedError

    def process_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Process a pending inbound payment.
        Coordinates: Provider Verification → Treasury → Accounting.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            InboundPaymentRead: Updated payment with processing status.
        
        Raises:
            NotFoundError: If the payment does not exist.
            ValidationError: If payment cannot be processed.
        """
        raise NotImplementedError

    def verify_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Verify an inbound payment with the provider.
        
        Args:
            payment_id (UUID): Payment identifier.
        
        Returns:
            InboundPaymentRead: Updated payment with verification status.
        
        Raises:
            NotFoundError: If the payment does not exist.
        """
        raise NotImplementedError


class InboundPaymentAdapter(InboundPaymentPort):
    """
    Adapter implementation of InboundPaymentPort.
    Delegates all inbound payment operations to InboundPaymentProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: InboundPaymentProvider):
        """
        Initialize the adapter with an inbound payment provider.
        
        Args:
            provider (InboundPaymentProvider): The data provider for inbound payment operations.
        """
        self.provider = provider

    def create_inbound_payment(self, payment_in: InboundPaymentCreate) -> InboundPaymentRead:
        """
        Create inbound payment via provider implementation.
        """
        payment_model = self.provider.create_inbound_payment(cast(Any, payment_in))
        return InboundPaymentRead.model_validate(payment_model)

    def get_inbound_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Retrieve inbound payment by ID via provider implementation.
        """
        payment_model = self.provider.get_inbound_payment(payment_id)
        return InboundPaymentRead.model_validate(payment_model)

    def get_payment_by_number(self, payment_number: str) -> InboundPaymentRead:
        """
        Retrieve inbound payment by payment number via provider implementation.
        """
        payment_model = self.provider.get_payment_by_number(payment_number)
        return InboundPaymentRead.model_validate(payment_model)

    def get_payment_by_provider_reference(self, provider_reference: str) -> InboundPaymentRead:
        """
        Retrieve inbound payment by provider reference via provider implementation.
        """
        payment_model = self.provider.get_payment_by_provider_reference(provider_reference)
        return InboundPaymentRead.model_validate(payment_model)

    def list_inbound_payments(
        self, 
        destination_account_id: UUID | None = None,
        status: str | None = None
    ) -> List[InboundPaymentRead]:
        """
        List inbound payments via provider, optionally filtered.
        """
        payments = self.provider.list_inbound_payments(destination_account_id, status)
        return [InboundPaymentRead.model_validate(payment) for payment in payments]

    def process_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Process payment via provider implementation.
        Provider coordinates with verification, treasury, and accounting.
        """
        payment_model = self.provider.process_payment(payment_id)
        return InboundPaymentRead.model_validate(payment_model)

    def verify_payment(self, payment_id: UUID) -> InboundPaymentRead:
        """
        Verify payment via provider implementation.
        """
        payment_model = self.provider.verify_payment(payment_id)
        return InboundPaymentRead.model_validate(payment_model)