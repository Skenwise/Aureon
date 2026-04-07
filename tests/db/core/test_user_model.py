# tests/db/test_user_model.py
"""Integration tests for User model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.user import User
from database.model.security.role import SecurityRole


def test_create_user(db_session):
    """Create a valid User record and verify it persists correctly."""
    # First create a role (parent record for foreign key)
    role = SecurityRole(name="admin", description="Administrator", is_default=False)
    db_session.add(role)
    db_session.commit()

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here",
        full_name="Test User",
        is_active=True,
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    retrieved = db_session.get(User, user.id)
    assert retrieved is not None
    assert retrieved.username == "testuser"
    assert retrieved.email == "test@example.com"
    assert retrieved.full_name == "Test User"
    assert retrieved.is_active is True
    assert retrieved.role_id == role.id


def test_user_unique_constraints(db_session):
    """Duplicate username should raise IntegrityError."""
    role = SecurityRole(name="default_role", is_default=True)
    db_session.add(role)
    db_session.commit()

    user1 = User(username="uniqueuser", email="user1@example.com", hashed_password="hash1")
    user2 = User(username="uniqueuser", email="user2@example.com", hashed_password="hash2")

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_user_relationships(db_session):
    """Test User to Role relationship works correctly."""
    # Create parent Role
    role = SecurityRole(name="editor", description="Can edit content", is_default=False)
    db_session.add(role)
    db_session.commit()

    # Create User linked to Role
    user = User(
        username="editoruser",
        email="editor@example.com",
        hashed_password="hash",
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()

    # Verify relationship
    assert user.role is not None
    assert user.role.id == role.id
    assert user.role.name == "editor"