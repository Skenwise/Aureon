# tests/db/payments/test_subscription_model.py
"""Integration tests for Subscription model using isolated database harness."""

from datetime import date, timedelta

from database.model.core.company import Company
from database.model.payments.subscription import Subscription


def test_create_subscription(db_session):
    """Create a valid Subscription record and verify it persists correctly."""
    company = Company(code="SUBCO", name="Subscription Company")
    db_session.add(company)
    db_session.commit()

    start_date = date.today()
    end_date = start_date + timedelta(days=365)

    subscription = Subscription(
        company_id=company.id,
        plan_name="Enterprise",
        status="active",
        start_date=start_date,
        end_date=end_date,
        auto_renew=True
    )
    db_session.add(subscription)
    db_session.commit()

    retrieved = db_session.get(Subscription, subscription.id)
    assert retrieved is not None
    assert retrieved.plan_name == "Enterprise"
    assert retrieved.status == "active"
    assert retrieved.auto_renew is True


def test_subscription_relationships(db_session):
    """Test Subscription to Company relationship."""
    company = Company(code="RELSUB", name="Relationship Subscription Co")
    db_session.add(company)
    db_session.commit()

    subscription = Subscription(
        company_id=company.id,
        plan_name="Basic",
        status="active"
    )
    db_session.add(subscription)
    db_session.commit()

    assert subscription.company is not None
    assert subscription.company.id == company.id
    assert subscription.company.name == "Relationship Subscription Co"