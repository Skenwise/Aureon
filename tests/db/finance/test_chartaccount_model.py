# tests/db/test_chartaccount_model.py
"""Integration tests for ChartAccount model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.finance.chart_of_account import ChartAccount


def test_create_chart_account(db_session):
    """Create a valid ChartAccount record and verify it persists correctly."""
    account = ChartAccount(
        code="1000",
        name="Cash",
        account_type="ASSET",
        description="Cash on hand"
    )
    db_session.add(account)
    db_session.commit()

    retrieved = db_session.get(ChartAccount, account.id)
    assert retrieved is not None
    assert retrieved.code == "1000"
    assert retrieved.name == "Cash"
    assert retrieved.account_type == "ASSET"


def test_chart_account_unique_constraints(db_session):
    """Duplicate code should raise IntegrityError."""
    account1 = ChartAccount(code="DUPLICATE", name="First Account", account_type="ASSET")
    account2 = ChartAccount(code="DUPLICATE", name="Second Account", account_type="LIABILITY")

    db_session.add(account1)
    db_session.commit()

    db_session.add(account2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_chart_account_self_referential_relationship(db_session):
    """Test parent-child relationship for ChartAccount."""
    parent = ChartAccount(
        code="4000",
        name="Revenue",
        account_type="INCOME",
        description="Parent account"
    )
    db_session.add(parent)
    db_session.commit()

    child = ChartAccount(
        code="4100",
        name="Interest Income",
        account_type="INCOME",
        parent_account_id=parent.id,
        description="Child account"
    )
    db_session.add(child)
    db_session.commit()

    # Verify relationship
    assert child.parent is not None
    assert child.parent.id == parent.id
    assert parent.children is not None
    assert len(parent.children) == 1
    assert parent.children[0].id == child.id