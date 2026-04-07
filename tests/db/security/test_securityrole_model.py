# tests/db/security/test_securityrole_model.py
"""Integration tests for SecurityRole model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.security.role import SecurityRole


def test_create_security_role(db_session):
    """Create a valid SecurityRole record and verify it persists correctly."""
    role = SecurityRole(
        name="admin",
        description="Administrator with full access",
        is_default=False
    )
    db_session.add(role)
    db_session.commit()

    retrieved = db_session.get(SecurityRole, role.id)
    assert retrieved is not None
    assert retrieved.name == "admin"
    assert retrieved.description == "Administrator with full access"
    assert retrieved.is_default is False


def test_security_role_unique_constraints(db_session):
    """Duplicate role name should raise IntegrityError."""
    role1 = SecurityRole(name="manager", is_default=False)
    role2 = SecurityRole(name="manager", is_default=True)

    db_session.add(role1)
    db_session.commit()

    db_session.add(role2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_security_role_default_value(db_session):
    """Test that is_default defaults to False."""
    role = SecurityRole(name="default_test_role")
    db_session.add(role)
    db_session.commit()

    retrieved = db_session.get(SecurityRole, role.id)
    assert retrieved.is_default is False