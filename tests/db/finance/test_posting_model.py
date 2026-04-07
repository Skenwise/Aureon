# tests/db/test_posting_model.py
"""Integration tests for Posting model using isolated database harness."""

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.finance.account import Account
from database.model.finance.journal import Journal
from database.model.finance.posting import Posting


def test_create_posting(db_session):
    """Create a valid Posting record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="POSTCO", name="Posting Company")
    account = Account(account_number="1000", account_type="ASSET", currency="USD")
    journal = Journal(reference="POST-001", total_debit=100, total_credit=100, currency="USD", source="TEST")
    
    db_session.add_all([currency, company, account, journal])
    db_session.commit()

    posting = Posting(
        journal_id=journal.id,
        account_id=account.id,
        amount=100.00,
        entry_type="debit",
        currency="USD",
        description="Test posting"
    )
    db_session.add(posting)
    db_session.commit()

    retrieved = db_session.get(Posting, posting.id)
    assert retrieved is not None
    assert retrieved.amount == 100.00
    assert retrieved.entry_type == "debit"


def test_posting_relationships(db_session):
    """Test Posting to Journal and Account relationships."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELPOST", name="Relationship Posting Co")
    account = Account(account_number="2000", account_type="LIABILITY", currency="ZMW")
    journal = Journal(reference="REL-002", total_debit=50, total_credit=50, currency="ZMW", source="TEST")
    
    db_session.add_all([currency, company, account, journal])
    db_session.commit()

    posting = Posting(
        journal_id=journal.id,
        account_id=account.id,
        amount=50.00,
        entry_type="credit",
        currency="ZMW"
    )
    db_session.add(posting)
    db_session.commit()

    assert posting.journal is not None
    assert posting.journal.id == journal.id
    assert posting.account is not None
    assert posting.account.id == account.id