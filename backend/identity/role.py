# backend/identity/role.py

"""
Identity Role Port & Adapter.

Defines role retrieval and mapping operations in the Identity module.
Roles are immutable authority constructs used to assign permissions to users.
"""

from typing import Protocol, List, Optional
from uuid import UUID
from schemas.roleSchema import RoleRead
from Middleware.DataProvider.IdentityProvider.roleProvider import SecurityRoleProvider
from backend.core.error import NotFoundError


class RolePort(Protocol):
    """
    Port interface for role operations.

    Roles are immutable; this interface defines read-only
    access patterns for identity and authorization services.
    """

    def get_role_by_id(self, role_id: str) -> RoleRead:
        """
        Retrieve a role by its unique ID.

        Args:
            role_id (str): Unique identifier for the role.

        Returns:
            RoleRead: The role representation.

        Raises:
            NotFoundError: If the role does not exist.
        """
        raise NotImplementedError

    def get_role_by_name(self, name: str) -> RoleRead:
        """
        Retrieve a role by its unique name.

        Args:
            name (str): Name of the role.

        Returns:
            RoleRead: The role representation.

        Raises:
            NotFoundError: If the role does not exist.
        """
        raise NotImplementedError

    def list_roles(self, permission_filter: Optional[str] = None) -> List[RoleRead]:
        """
        List all roles, optionally filtered by a specific permission code.

        Args:
            permission_filter (str, optional): Return only roles that contain this permission.

        Returns:
            List[RoleRead]: List of role representations.
        """
        raise NotImplementedError

class RoleAdapter(RolePort):
    """
    Adapter implementing the RolePort.

    Translates identity-layer role queries into
    security role provider operations.
    """

    def __init__(self, provider: SecurityRoleProvider) -> None:
        """
        Initialize the adapter with a security role provider.

        Args:
            provider (SecurityRoleProvider): Read-only role provider.
        """
        self._provider = provider

    def get_role_by_id(self, role_id: str) -> RoleRead:
        role = self._provider.get_by_id(UUID(role_id))
        if role is None:
            raise NotFoundError("Role", role_id)

        return RoleRead.model_validate(role)

    def get_role_by_name(self, name: str) -> RoleRead:
        role = self._provider.get_by_name(name)
        if role is None:
            raise NotFoundError("Role", name)

        return RoleRead.model_validate(role)

    def list_roles(self, permission_filter: Optional[str] = None) -> List[RoleRead]:
        roles = self._provider.list_all()

        if permission_filter:
            roles = [
                role for role in roles
                if permission_filter in role.permissions
            ]

        return [RoleRead.model_validate(role) for role in roles]
