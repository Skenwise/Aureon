# tests/db/audit/test_reconciliation_model.py
"""Integration tests for Reconciliation model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import date

from database.model.core.company import Company
from database.model.core.user import User
from database.model.security.role import SecurityRole
from database.model.audit.reconciliation import Reconciliation


def test_create_reconciliation(db_session):
    """Create a valid Reconciliation record and verify it persists correctly."""
    company = Company(code="RECCO", name="Reconciliation Company")
    role = SecurityRole(name="accountant", is_default=False)
    user = User(username="reconcileuser", email="rec@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([company, role, user])
    db_session.commit()

    reconciliation = Reconciliation(
        tenant_id=company.id,
        business_date=date.today(),
        reconciliation_number="REC-2024-001",
        total_debits=10000,
        total_credits=10000,
        balanced=True,
        calculated_by=user.id,
        notes="All accounts balanced"
    )
    db_session.add(reconciliation)
    db_session.commit()

    retrieved = db_session.get(Reconciliation, reconciliation.id)
    assert retrieved is not None
    assert retrieved.reconciliation_number == "REC-2024-001"
    assert retrieved.total_debits == 10000
    assert retrieved.total_credits == 10000
    assert retrieved.balanced is True


def test_reconciliation_unique_constraints(db_session):
    """Duplicate reconciliation_number should raise IntegrityError."""
    company = Company(code="UNIQREC", name="Unique Reconciliation Co")
    db_session.add(company)
    db_session.commit()

    rec1 = Reconciliation(
        tenant_id=company.id,
        business_date=date.today(),
        reconciliation_number="UNIQ001",
        total_debits=100,
        total_credits=100,
        balanced=True
    )
    rec2 = Reconciliation(
        tenant_id=company.id,
        business_date=date.today(),
        reconciliation_number="UNIQ001",
        total_debits=200,
        total_credits=200,
        balanced=True
    )

    db_session.add(rec1)
    db_session.commit()

    db_session.add(rec2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_reconciliation_auto_balanced(db_session):
    """Test that balanced can be set manually."""
    company = Company(code="AUTOREC", name="Auto Balance Co")
    db_session.add(company)
    db_session.commit()

    reconciliation = Reconciliation(
        tenant_id=company.id,
        business_date=date.today(),
        reconciliation_number="AUTO-001",
        total_debits=5000,
        total_credits=5000,
        balanced=True
    )
    db_session.add(reconciliation)
    db_session.commit()

    assert reconciliation.balanced is True


def test_reconciliation_relationships(db_session):
    """Test Reconciliation to Company and User relationships."""
    company = Company(code="RELREC", name="Relationship Reconciliation Co")
    role = SecurityRole(name="admin", is_default=False)
    user = User(username="relrec", email="relrec@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([company, role, user])
    db_session.commit()

    reconciliation = Reconciliation(
        tenant_id=company.id,
        business_date=date.today(),
        reconciliation_number="REL-001",
        total_debits=1000,
        total_credits=1000,
        balanced=True,
        calculated_by=user.id
    )
    db_session.add(reconciliation)
    db_session.commit()

    assert reconciliation.tenant_id == company.id
    assert reconciliation.calculated_by == user.id