# backend/tenants/context.py
"""
Tenant Context Management for Aureon Multi-Tenant System

This module provides tenant context management, allowing the application to:
- Track the current active tenant
- Provide tenant-scoped dependency injection
- Manage tenant-specific configurations and services
- Ensure proper tenant isolation throughout the request lifecycle
"""

from typing import Optional
from uuid import UUID
from contextvars import ContextVar
from Middleware.DataProvider.TenantProvider import TenantProvider
from .tenant import TenantService
from schemas.tenantSchema import TenantRead


# Context variable to store current tenant ID across async calls
_current_tenant_id: ContextVar[Optional[UUID]] = ContextVar('current_tenant_id', default=None)


class TenantContext:
    """
    Manages tenant-specific context and provides access to tenant-scoped services.

    This class acts as a dependency injection container for tenant-specific operations,
    ensuring that all operations are properly scoped to the current tenant.
    """

    def __init__(self, provider: TenantProvider):
        """
        Initialize tenant context with a data provider.

        Args:
            provider: TenantProvider instance for database operations
        """
        self.provider = provider
        self._service: Optional[TenantService] = None

    @property
    def service(self) -> TenantService:
        """Get the tenant service for the current context."""
        if self._service is None:
            self._service = TenantService(self.provider)
        return self._service

    @property
    def current_tenant_id(self) -> Optional[UUID]:
        """Get the current tenant ID from context."""
        return _current_tenant_id.get()

    @property
    def current_tenant(self) -> Optional[TenantRead]:
        """Get the current tenant information."""
        tenant_id = self.current_tenant_id
        if tenant_id:
            return self.service.get_tenant_by_id(tenant_id)
        return None

    def set_current_tenant(self, tenant_id: UUID) -> None:
        """
        Set the current tenant for this context.

        Args:
            tenant_id: The UUID of the tenant to set as current
        """
        _current_tenant_id.set(tenant_id)

    def clear_current_tenant(self) -> None:
        """Clear the current tenant from context."""
        _current_tenant_id.set(None)

    def get_tenant_service_for(self, tenant_id: UUID) -> TenantService:
        """
        Get a tenant service scoped to a specific tenant.

        This is useful when you need to operate on behalf of a different tenant
        than the current context tenant.

        Args:
            tenant_id: The tenant ID to scope the service to

        Returns:
            A TenantService instance configured for the specified tenant
        """
        # For now, return the same service since TenantService doesn't store tenant state
        # In a more complex implementation, this could return a tenant-scoped service
        return self.service


class TenantContextManager:
    """
    Context manager for tenant operations.

    Usage:
        with TenantContextManager(context, tenant_id) as tenant_ctx:
            # Operations here are scoped to the specified tenant
            tenant = tenant_ctx.current_tenant
    """

    def __init__(self, context: TenantContext, tenant_id: UUID):
        """
        Initialize the context manager.

        Args:
            context: The tenant context to manage
            tenant_id: The tenant ID to set for the duration
        """
        self.context = context
        self.tenant_id = tenant_id
        self.previous_tenant_id = None

    def __enter__(self) -> TenantContext:
        """Enter the context, setting the tenant."""
        self.previous_tenant_id = self.context.current_tenant_id
        self.context.set_current_tenant(self.tenant_id)
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context, restoring the previous tenant."""
        if self.previous_tenant_id is not None:
            self.context.set_current_tenant(self.previous_tenant_id)
        else:
            self.context.clear_current_tenant()