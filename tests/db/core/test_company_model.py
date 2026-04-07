# tests/db/test_company_model.py
"""Integration tests for Company model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.company import Company


def test_create_company(db_session):
    """Create a valid Company record and verify it persists correctly."""
    company = Company(
        code="TESTCO",
        name="Test Company",
        timezone="Africa/Lusaka",
        currency="ZMW",
        subscription_tier="premium",
        subscription_status="active",
        note="Test note"
    )
    db_session.add(company)
    db_session.commit()

    retrieved = db_session.get(Company, company.id)
    assert retrieved is not None
    assert retrieved.code == "TESTCO"
    assert retrieved.name == "Test Company"
    assert retrieved.timezone == "Africa/Lusaka"
    assert retrieved.currency == "ZMW"
    assert retrieved.subscription_tier == "premium"
    assert retrieved.subscription_status == "active"
    assert retrieved.note == "Test note"


def test_company_unique_constraints(db_session):
    """Duplicate company code should raise IntegrityError."""
    company1 = Company(code="DUPLICATE", name="First Company")
    company2 = Company(code="DUPLICATE", name="Second Company")

    db_session.add(company1)
    db_session.commit()

    db_session.add(company2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()