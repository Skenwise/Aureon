# backend/payments/providers/registry.py
"""
Payment Provider Registry.

Maps payment requests to the correct execution provider.
Acts as a factory and resolver for provider instances.

This prevents hardcoding providers in business logic.
Critical for scalability and maintainability.
"""

from typing import Dict, Type, Optional
from enum import Enum

from backend.payments.provider.base import PaymentProviderBase
from backend.payments.provider.internal import InternalProvider


class ProviderType(str, Enum):
    """
    Supported provider types.
    Add new providers here as they're implemented.
    """
    INTERNAL = "INTERNAL"
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK = "BANK"
    CARD = "CARD"


class PaymentProviderRegistry:
    """
    Provider registry and factory.
    
    Responsibilities:
    - Register available providers
    - Resolve provider by type
    - Create provider instances
    - Manage provider configuration
    
    Usage:
        registry = PaymentProviderRegistry()
        provider = registry.get_provider(ProviderType.INTERNAL)
        result = provider.execute_outbound(...)
    """
    
    def __init__(self):
        """Initialize provider registry."""
        self._providers: Dict[str, Type[PaymentProviderBase]] = {}
        self._instances: Dict[str, PaymentProviderBase] = {}
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register default built-in providers."""
        # Register internal provider
        self.register_provider(ProviderType.INTERNAL, InternalProvider)
        
        # Future providers will be registered here:
        # self.register_provider(ProviderType.MOBILE_MONEY, MTNProvider)
        # self.register_provider(ProviderType.BANK, BankProvider)
    
    def register_provider(
        self,
        provider_type: ProviderType,
        provider_class: Type[PaymentProviderBase]
    ):
        """
        Register a provider class for a given type.
        
        Args:
            provider_type (ProviderType): Provider type identifier.
            provider_class (Type[PaymentProviderBase]): Provider class to register.
        """
        self._providers[provider_type.value] = provider_class
    
    def get_provider(
        self,
        provider_type: ProviderType,
        config: Optional[Dict] = None
    ) -> PaymentProviderBase:
        """
        Get or create provider instance.
        
        Providers are cached as singletons per type.
        
        Args:
            provider_type (ProviderType): Provider type to retrieve.
            config (dict, optional): Provider configuration.
        
        Returns:
            PaymentProviderBase: Provider instance.
        
        Raises:
            ValueError: If provider type is not registered.
        """
        provider_key = provider_type.value
        
        # Check if provider is registered
        if provider_key not in self._providers:
            raise ValueError(f"Provider type '{provider_key}' is not registered")
        
        # Return cached instance if exists
        if provider_key in self._instances:
            return self._instances[provider_key]
        
        # Create new instance
        provider_class = self._providers[provider_key]
        
        # Instantiate provider (internal provider takes no config)
        provider_instance = provider_class(provider_name=provider_key, config=config)

        # Cache instance
        self._instances[provider_key] = provider_instance
        
        return provider_instance
    
    def resolve_provider_by_name(self, provider_name: str) -> PaymentProviderBase:
        """
        Resolve provider by string name.
        
        Useful for resolving from database records.
        
        Args:
            provider_name (str): Provider name (e.g., 'INTERNAL', 'MOBILE_MONEY').
        
        Returns:
            PaymentProviderBase: Provider instance.
        
        Raises:
            ValueError: If provider name is invalid.
        """
        try:
            provider_type = ProviderType(provider_name.upper())
            return self.get_provider(provider_type)
        except ValueError:
            raise ValueError(f"Unknown provider name: {provider_name}")
    
    def list_available_providers(self) -> list[str]:
        """
        List all registered provider types.
        
        Returns:
            list[str]: Available provider type names.
        """
        return list(self._providers.keys())
    
    def is_provider_available(self, provider_type: ProviderType) -> bool:
        """
        Check if a provider type is registered and operational.
        
        Args:
            provider_type (ProviderType): Provider type to check.
        
        Returns:
            bool: True if provider is available.
        """
        try:
            provider = self.get_provider(provider_type)
            return provider.is_available()
        except ValueError:
            return False


# Global registry instance
_registry: Optional[PaymentProviderRegistry] = None


def get_registry() -> PaymentProviderRegistry:
    """
    Get global provider registry instance.
    
    Returns:
        PaymentProviderRegistry: Global registry singleton.
    """
    global _registry
    if _registry is None:
        _registry = PaymentProviderRegistry()
    return _registry


def get_provider(provider_type: ProviderType) -> PaymentProviderBase:
    """
    Convenience function to get provider from global registry.
    
    Args:
        provider_type (ProviderType): Provider type to retrieve.
    
    Returns:
        PaymentProviderBase: Provider instance.
    """
    registry = get_registry()
    return registry.get_provider(provider_type)