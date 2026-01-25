# Middleware/DataProvider/TenantProvider.py
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from database.model.core.company import Company


class TenantProvider:
    """
    Data provider for tenant (Company) operations.
    Handles all database interactions for tenants.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session

    def create_tenant(self, tenant_data: dict) -> Company:
        """
        Create a new tenant in the database.

        Args:
            tenant_data: Dictionary of tenant data.

        Returns:
            The created Company instance.
        """
        tenant = Company(**tenant_data)
        self.session.add(tenant)
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Company]:
        """
        Retrieve a tenant by ID.

        Args:
            tenant_id: The UUID of the tenant.

        Returns:
            The Company instance if found, None otherwise.
        """
        return self.session.get(Company, tenant_id)

    def get_tenant_by_code(self, code: str) -> Optional[Company]:
        """
        Retrieve a tenant by code.

        Args:
            code: The unique code of the tenant.

        Returns:
            The Company instance if found, None otherwise.
        """
        statement = select(Company).where(Company.code == code)
        return self.session.exec(statement).first()

    def update_tenant(self, tenant: Company, update_data: dict) -> Company:
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
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def list_tenants(self) -> List[Company]:
        """
        List all tenants.

        Returns:
            List of all Company instances.
        """
        statement = select(Company)
        return list(self.session.exec(statement).all())

    def check_code_exists(self, code: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if a tenant code already exists.

        Args:
            code: The code to check.
            exclude_id: Optional ID to exclude from check (for updates).

        Returns:
            True if code exists, False otherwise.
        """
        query = select(Company).where(Company.code == code)
        if exclude_id:
            query = query.where(Company.id != exclude_id)
        return self.session.exec(query).first() is not None