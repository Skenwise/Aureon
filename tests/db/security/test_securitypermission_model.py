# tests/db/security/test_securitypermission_model.py
"""Integration tests for SecurityPermission model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.security.permission import SecurityPermission


def test_create_security_permission(db_session):
    """Create a valid SecurityPermission record and verify it persists correctly."""
    permission = SecurityPermission(
        name="loan.create",
        resource="loan",
        action="create",
        description="Ability to create loans"
    )
    db_session.add(permission)
    db_session.commit()

    retrieved = db_session.get(SecurityPermission, permission.id)
    assert retrieved is not None
    assert retrieved.name == "loan.create"
    assert retrieved.resource == "loan"
    assert retrieved.action == "create"
    assert retrieved.description == "Ability to create loans"


def test_security_permission_unique_constraints(db_session):
    """Duplicate permission name should raise IntegrityError."""
    permission1 = SecurityPermission(name="user.delete", resource="user", action="delete")
    permission2 = SecurityPermission(name="user.delete", resource="user", action="delete")

    db_session.add(permission1)
    db_session.commit()

    db_session.add(permission2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()