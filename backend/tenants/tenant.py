# backend/tenants/tenant.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from schemas.tenantSchema import TenantCreate, TenantUpdate, TenantRead
from Middleware.DataProvider.TenantProvider import TenantProvider
from backend.core.error import ValidationError


class TenantService:
    """
    Service class for managing tenants (Company entities).
    Contains business logic for tenant operations, delegating data access to TenantProvider.
    """

    def __init__(self, provider: TenantProvider):
        """
        Initialize the service with a tenant data provider.

        Args:
            provider: TenantProvider instance for data operations.
        """
        self.provider = provider

    def create_tenant(self, tenant_data: TenantCreate) -> TenantRead:
        """
        Create a new tenant with business logic validation.

        Args:
            tenant_data: Data for the new tenant.

        Returns:
            The created tenant.

        Raises:
            ValidationError: If a tenant with the same code already exists.
        """
        # Business logic: Check for unique code
        if self.provider.check_code_exists(tenant_data.code):
            raise ValidationError(f"Tenant with code '{tenant_data.code}' already exists")
        
        # Delegate creation to provider
        tenant = self.provider.create_tenant(tenant_data.model_dump())
        return TenantRead(**tenant.model_dump())

    def get_tenant_by_id(self, tenant_id: UUID) -> Optional[TenantRead]:
        """
        Retrieve a tenant by its ID.

        Args:
            tenant_id: The UUID of the tenant.

        Returns:
            The tenant if found, None otherwise.
        """
        tenant = self.provider.get_tenant_by_id(tenant_id)
        if tenant:
            return TenantRead(**tenant.model_dump())
        return None

    def get_tenant_by_code(self, code: str) -> Optional[TenantRead]:
        """
        Retrieve a tenant by its code.

        Args:
            code: The unique code of the tenant.

        Returns:
            The tenant if found, None otherwise.
        """
        tenant = self.provider.get_tenant_by_code(code)
        if tenant:
            return TenantRead(**tenant.model_dump())
        return None

    def update_tenant(self, tenant_id: UUID, update_data: TenantUpdate) -> Optional[TenantRead]:
        """
        Update an existing tenant with business logic validation.

        Args:
            tenant_id: The UUID of the tenant to update.
            update_data: The data to update.

        Returns:
            The updated tenant if found, None otherwise.

        Raises:
            ValidationError: If updating to a code that already exists.
        """
        tenant = self.provider.get_tenant_by_id(tenant_id)
        if not tenant:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Business logic: Check unique code if updating code
        if 'code' in update_dict:
            new_code = update_dict['code']
            if self.provider.check_code_exists(new_code, exclude_id=tenant_id):
                raise ValidationError(f"Tenant with code '{new_code}' already exists")

        # Apply business logic for timestamps
        update_dict['updated_at'] = datetime.utcnow()

        # Delegate update to provider
        updated_tenant = self.provider.update_tenant(tenant, update_dict)
        return TenantRead(**updated_tenant.model_dump())

    def list_tenants(self) -> List[TenantRead]:
        """
        List all tenants.

        Returns:
            A list of all tenants.
        """
        tenants = self.provider.list_tenants()
        return [TenantRead(**tenant.model_dump()) for tenant in tenants]