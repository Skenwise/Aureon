# tests/db/test_journal_model.py
"""Integration tests for Journal model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.company import Company
from database.model.core.user import User
from database.model.misc.currency import Currency
from database.model.finance.journal import Journal
from database.model.security.role import SecurityRole


def test_create_journal(db_session):
    """Create a valid Journal record and verify it persists correctly."""
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="JRNCO", name="Journal Company")
    role = SecurityRole(name="admin", is_default=True)
    user = User(username="journaluser", email="journal@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([currency, company, role, user])
    db_session.commit()

    journal = Journal(
        reference="JRN-2024-001",
        description="Test journal entry",
        total_debit=500.00,
        total_credit=500.00,
        currency="USD",
        created_by=user.id,
        status="posted",
        source="TEST_MODULE"
    )
    db_session.add(journal)
    db_session.commit()

    retrieved = db_session.get(Journal, journal.id)
    assert retrieved is not None
    assert retrieved.reference == "JRN-2024-001"
    assert retrieved.total_debit == 500.00
    assert retrieved.total_credit == 500.00


def test_journal_unique_constraints(db_session):
    """Duplicate reference should raise IntegrityError."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="UNIQJRN", name="Unique Journal Co")
    db_session.add_all([currency, company])
    db_session.commit()

    journal1 = Journal(reference="UNIQ001", total_debit=0, total_credit=0, currency="ZMW", source="TEST")
    journal2 = Journal(reference="UNIQ001", total_debit=0, total_credit=0, currency="ZMW", source="TEST")

    db_session.add(journal1)
    db_session.commit()

    db_session.add(journal2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_journal_relationships(db_session):
    """Test Journal to Company and User relationships."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="RELJRN", name="Relationship Journal Co")
    role = SecurityRole(name="editor", is_default=False)
    user = User(username="journalcreator", email="creator@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([currency, company, role, user])
    db_session.commit()

    journal = Journal(
        reference="REL-001",
        total_debit=0,
        total_credit=0,
        currency="EUR",
        created_by=user.id,
        source="TEST",
        company_id=company.id  # ← Added
    )
    db_session.add(journal)
    db_session.commit()

    assert journal.company is not None
    assert journal.company.id == company.id
    assert journal.creator is not None
    assert journal.creator.id == user.id