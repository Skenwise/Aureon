# backend/identity/permission.py

"""
Identity Permission Port.

Defines authorization decision contracts.
Permissions are evaluated deterministically and are read-only.
"""

from typing import Protocol
from backend.core.error import AuthorizationError
from backend.core.error import AuthorizationError
from Middleware.DataProvider.IdentityProvider.permissionProvider import SecurityPermissionProvider
from .permission import PermissionPort
from uuid import UUID


class PermissionPort(Protocol):
    """
    Port interface for permission checks.

    This port answers authorization questions without
    mutating state or depending on infrastructure details.
    """

    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Check whether a user has a specific permission.

        Args:
            user_id (str): Unique identifier of the user.
            permission (str): Permission code to check.

        Returns:
            bool: True if allowed, False otherwise.
        """
        raise NotImplementedError

    def assert_permission(self, user_id: str, permission: str) -> None:
        """
        Assert that a user has a specific permission.

        Args:
            user_id (str): Unique identifier of the user.
            permission (str): Permission code to check.

        Raises:
            AuthorizationError: If the permission is not granted.
        """
        raise NotImplementedError
    


class PermissionAdapter(PermissionPort):
    """
    Permission Adapter.

    Implements PermissionPort using SecurityPermissionProvider.
    Handles deterministic read-only permission checks for internal users.

    Adapter implementing permission checks.

    Delegates actual permission lookups to SecurityPermissionProvider.
    """

    def __init__(self, provider: SecurityPermissionProvider):
        """
        Initialize adapter with a provider.

        Args:
            provider (SecurityPermissionProvider): Handles DB queries for permissions.
        """
        self.provider = provider

    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if the user has the given permission.

        Args:
            user_id (str): Unique identifier of the user.
            permission (str): Permission code.

        Returns:
            bool: True if the permission exists for the user, False otherwise.
        """
        return self.provider.user_has_permission(UUID(user_id), permission)

    def assert_permission(self, user_id: str, permission: str) -> None:
        """
        Ensure that a user has a specific permission.

        Args:
            user_id (str): Unique identifier of the user.
            permission (str): Permission code.

        Raises:
            AuthorizationError: If the user does not have the permission.
        """
        if not self.has_permission(user_id, permission):
            raise AuthorizationError(
                f"User '{user_id}' lacks required permission '{permission}'"
            )

