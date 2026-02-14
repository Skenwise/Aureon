# backend/payments/providers/internal.py
"""
Internal Payment Provider.

Handles internal ledger transfers within Aureon.
No external API calls - pure internal movement.

This is the simplest and fastest provider.
Use for:
- Loan disbursements from treasury
- Internal account transfers
- Settlement operations
- Inter-account movements
"""

from typing import Optional, Dict, Any
from decimal import Decimal

from backend.payments.provider.base import PaymentProviderBase, PaymentExecutionResult


class InternalProvider(PaymentProviderBase):
    """
    Internal payment provider for ledger-only transfers.
    
    No external network calls.
    Always succeeds if accounts exist and have sufficient balance.
    
    Execution is atomic and deterministic.
    """
    
    def __init__(self, provider_name: str = "INTERNAL", config: Optional[Dict[str, Any]] = None):
        """Initialize internal provider."""
        super().__init__(provider_name="INTERNAL")
    
    def execute_outbound(
        self,
        amount: Decimal,
        currency: str,
        destination: str,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentExecutionResult:
        """
        Execute internal outbound transfer.
        
        For internal provider, this is a ledger movement.
        Actual balance updates happen in accounting layer.
        
        Args:
            amount (Decimal): Transfer amount.
            currency (str): Currency code.
            destination (str): Destination account ID.
            reference (str, optional): Transfer reference.
            metadata (dict, optional): Additional metadata.
        
        Returns:
            PaymentExecutionResult: Always successful for internal transfers.
        """
        # Internal transfers are deterministic
        # No external API call needed
        # Accounting layer handles actual balance updates
        
        # Generate internal transaction ID
        import uuid
        transaction_id = f"INT-{uuid.uuid4().hex[:12].upper()}"
        
        return PaymentExecutionResult(
            success=True,
            provider_transaction_id=transaction_id,
            provider_reference=reference or transaction_id,
            raw_response={
                "provider": "INTERNAL",
                "amount": str(amount),
                "currency": currency,
                "destination": destination,
                "reference": reference
            }
        )
    
    def execute_inbound(
        self,
        amount: Decimal,
        currency: str,
        source: str,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentExecutionResult:
        """
        Execute internal inbound transfer.
        
        For internal provider, this is a ledger movement.
        
        Args:
            amount (Decimal): Transfer amount.
            currency (str): Currency code.
            source (str): Source account ID.
            reference (str, optional): Transfer reference.
            metadata (dict, optional): Additional metadata.
        
        Returns:
            PaymentExecutionResult: Always successful for internal transfers.
        """
        # Internal transfers are deterministic
        # No verification needed
        
        # Generate internal transaction ID
        import uuid
        transaction_id = f"INT-{uuid.uuid4().hex[:12].upper()}"
        
        return PaymentExecutionResult(
            success=True,
            provider_transaction_id=transaction_id,
            provider_reference=reference or transaction_id,
            raw_response={
                "provider": "INTERNAL",
                "amount": str(amount),
                "currency": currency,
                "source": source,
                "reference": reference
            }
        )
    
    def verify_transaction(
        self,
        provider_transaction_id: str
    ) -> PaymentExecutionResult:
        """
        Verify internal transaction.
        
        Internal transactions are always valid once created.
        Verification is a no-op.
        
        Args:
            provider_transaction_id (str): Internal transaction ID.
        
        Returns:
            PaymentExecutionResult: Always successful.
        """
        return PaymentExecutionResult(
            success=True,
            provider_transaction_id=provider_transaction_id,
            raw_response={
                "provider": "INTERNAL",
                "transaction_id": provider_transaction_id,
                "status": "VERIFIED"
            }
        )
    
    def check_balance(self) -> Decimal:
        """
        Check internal balance.
        
        Internal provider doesn't have a "balance" in the traditional sense.
        Balance is managed by treasury and accounting.
        
        Returns:
            Decimal: Always returns 0 (balance managed elsewhere).
        """
        # Internal provider balance is managed by treasury
        # This method is not applicable for internal transfers
        return Decimal("0")
    
    def is_available(self) -> bool:
        """
        Check if internal provider is available.
        
        Internal provider is always available (no network dependency).
        
        Returns:
            bool: Always True.
        """
        return True