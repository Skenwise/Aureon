#Middleware/DataProvider/IdentityProvider/roleProvider.py

"""
Security role provider.

Provides read-only access to immutable security roles.
Acts as the persistence boundary for role-based authorization.
"""

from typing import Optional, List
from uuid import UUID

from sqlmodel import Session, select

from database.model.security.role import SecurityRole


class SecurityRoleProvider:
    """
    Read-only provider for security roles.

    This provider enforces immutability by exposing only
    retrieval and resolution operations.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the role provider.

        Args:
            session: Active database session.
        """
        self._session = session

    def get_by_id(self, role_id: UUID) -> Optional[SecurityRole]:
        """
        Retrieve a role by its unique identifier.

        Args:
            role_id: Role UUID.

        Returns:
            The SecurityRole if found, otherwise None.
        """
        statement = select(SecurityRole).where(SecurityRole.id == role_id)
        return self._session.exec(statement).one_or_none()

    def get_by_name(self, name: str) -> Optional[SecurityRole]:
        """
        Retrieve a role by its unique name.

        Args:
            name: Role name.

        Returns:
            The SecurityRole if found, otherwise None.
        """
        statement = select(SecurityRole).where(SecurityRole.name == name)
        return self._session.exec(statement).one_or_none()

    def list_all(self) -> List[SecurityRole]:
        """
        List all defined security roles.

        Returns:
            List of all SecurityRole records.
        """
        statement = select(SecurityRole)
        return list(self._session.exec(statement).all())

    def resolve_permissions(self, role_id: UUID) -> List[str]:
        """
        Resolve permission codes for a given role.

        Args:
            role_id: Role UUID.

        Returns:
            List of permission codes.

        Raises:
            ValueError: If the role does not exist.
        """
        role = self.get_by_id(role_id)
        if role is None:
            raise ValueError(f"SecurityRole not found: {role_id}")

        return list(role.permissions)
