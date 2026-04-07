from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from database.model.core.company import Company


class TenantProvider:
    """
    Data provider for tenant (Company) operations.
    Handles all database interactions for tenants.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session

    async def create_tenant(self, tenant_data: dict) -> Company:
        """
        Create a new tenant in the database.

        Args:
            tenant_data: Dictionary of tenant data.

        Returns:
            The created Company instance.
        """
        tenant = Company(**tenant_data)
        self.session.add(tenant)
        await self.session.commit()
        await self.session.refresh(tenant)
        return tenant

    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Company]:
        """
        Retrieve a tenant by ID.

        Args:
            tenant_id: The UUID of the tenant.

        Returns:
            The Company instance if found, None otherwise.
        """
        return await self.session.get(Company, tenant_id)

    async def get_tenant_by_code(self, code: str) -> Optional[Company]:
        """
        Retrieve a tenant by code.

        Args:
            code: The unique code of the tenant.

        Returns:
            The Company instance if found, None otherwise.
        """
        statement = select(Company).where(Company.code == code)  # type: ignore
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_tenant(self, tenant: Company, update_data: dict) -> Company:
        """
        Update an existing tenant.

        Args:
            tenant: The Company instance to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated Company instance.
        """
        for key, value in update_data.items():
            setattr(tenant, key, value)
        await self.session.commit()
        await self.session.refresh(tenant)
        return tenant

    async def list_tenants(self) -> List[Company]:
        """
        List all tenants.

        Returns:
            List of all Company instances.
        """
        statement = select(Company)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def check_code_exists(self, code: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if a tenant code already exists.

        Args:
            code: The code to check.
            exclude_id: Optional ID to exclude from check (for updates).

        Returns:
            True if code exists, False otherwise.
        """
        query = select(Company).where(Company.code == code)  # type: ignore
        if exclude_id:
            query = query.where(Company.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
