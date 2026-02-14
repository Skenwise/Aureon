# backend/payments/providers/base.py
"""
Base Payment Provider Interface.

Defines the contract that all payment execution providers must implement.
This is NOT a database provider - it's an execution abstraction layer.

Providers execute actual money movement via:
- Internal ledger transfers
- Mobile money APIs (MTN, Airtel, Zamtel)
- Bank transfer APIs
- Card processor APIs
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from decimal import Decimal


class PaymentExecutionResult:
    """
    Standard result from payment execution.
    Returned by all provider implementations.
    """
    
    def __init__(
        self,
        success: bool,
        provider_transaction_id: Optional[str] = None,
        provider_reference: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution result.
        
        Args:
            success (bool): Whether execution succeeded.
            provider_transaction_id (str, optional): Provider's transaction ID.
            provider_reference (str, optional): Provider's reference number.
            error_code (str, optional): Error code if failed.
            error_message (str, optional): Error message if failed.
            raw_response (dict, optional): Raw provider response for debugging.
        """
        self.success = success
        self.provider_transaction_id = provider_transaction_id
        self.provider_reference = provider_reference
        self.error_code = error_code
        self.error_message = error_message
        self.raw_response = raw_response or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "provider_transaction_id": self.provider_transaction_id,
            "provider_reference": self.provider_reference,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "raw_response": self.raw_response
        }


class PaymentProviderBase(ABC):
    """
    Abstract base class for payment execution providers.
    
    All providers must implement these methods.
    Providers are responsible for:
    - Executing actual fund transfers
    - Communicating with external APIs
    - Handling provider-specific logic
    - Returning standardized results
    
    Providers do NOT:
    - Create database records (that's DataProvider's job)
    - Update accounting (that's the adapter's job)
    - Check treasury liquidity (that's the adapter's job)
    """
    
    def __init__(self, provider_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider with configuration.
        
        Args:
            provider_name (str): Provider identifier (e.g., 'MTN', 'AIRTEL', 'INTERNAL').
            config (dict, optional): Provider-specific configuration.
        """
        self.provider_name = provider_name
        self.config = config or {}
    
    @abstractmethod
    def execute_outbound(
        self,
        amount: Decimal,
        currency: str,
        destination: str,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentExecutionResult:
        """
        Execute an outbound payment (money leaving system).
        
        Args:
            amount (Decimal): Payment amount.
            currency (str): ISO currency code (e.g., 'ZMW', 'USD').
            destination (str): Destination identifier (phone number, account number, etc.).
            reference (str, optional): Payment reference.
            metadata (dict, optional): Additional payment metadata.
        
        Returns:
            PaymentExecutionResult: Execution result with success status and details.
        
        Raises:
            Exception: If execution fails critically.
        """
        raise NotImplementedError
    
    @abstractmethod
    def execute_inbound(
        self,
        amount: Decimal,
        currency: str,
        source: str,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentExecutionResult:
        """
        Execute an inbound payment (money entering system).
        
        Note: For most providers, this is a verification step rather than execution.
        External systems push money to us, we verify it happened.
        
        Args:
            amount (Decimal): Payment amount.
            currency (str): ISO currency code.
            source (str): Source identifier (phone number, account number, etc.).
            reference (str, optional): Payment reference.
            metadata (dict, optional): Additional payment metadata.
        
        Returns:
            PaymentExecutionResult: Verification result.
        
        Raises:
            Exception: If verification fails critically.
        """
        raise NotImplementedError
    
    @abstractmethod
    def verify_transaction(
        self,
        provider_transaction_id: str
    ) -> PaymentExecutionResult:
        """
        Verify transaction status with provider.
        
        Used for:
        - Checking transaction completion
        - Reconciliation
        - Status updates
        
        Args:
            provider_transaction_id (str): Provider's transaction identifier.
        
        Returns:
            PaymentExecutionResult: Current transaction status.
        
        Raises:
            Exception: If verification fails critically.
        """
        raise NotImplementedError
    
    @abstractmethod
    def check_balance(self) -> Decimal:
        """
        Check available balance with provider.
        
        Returns:
            Decimal: Available balance.
        
        Raises:
            Exception: If balance check fails.
        """
        raise NotImplementedError
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.provider_name
    
    def is_available(self) -> bool:
        """
        Check if provider is currently available.
        
        Can be overridden for provider-specific health checks.
        
        Returns:
            bool: True if provider is operational.
        """
        return True