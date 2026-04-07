# tests/db/test_fee_model.py
"""Integration tests for Fee model using isolated database harness."""

from datetime import date, timedelta

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.loan import Loan
from database.model.finance.fees import Fee


def test_create_fee(db_session):
    """Create a valid Fee record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="FEECO", name="Fee Company")
    customer = Customer(first_name="Fee", last_name="Customer", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="FEE-001",
        principal_amount=10000,
        interest_rate=12,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="USD"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    fee = Fee(
        loan_id=loan.id,
        name="Late Payment Fee",
        amount=50.00,
        currency="USD",
        due_date=date.today() + timedelta(days=15),
        status="pending"
    )
    db_session.add(fee)
    db_session.commit()

    retrieved = db_session.get(Fee, fee.id)
    assert retrieved is not None
    assert retrieved.name == "Late Payment Fee"
    assert retrieved.amount == 50.00


def test_fee_relationships(db_session):
    """Test Fee to Loan relationship."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELFEE", name="Relationship Fee Co")
    customer = Customer(first_name="Rel", last_name="Fee", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="RELFEE-001",
        principal_amount=5000,
        interest_rate=10,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    fee = Fee(
        loan_id=loan.id,
        name="Processing Fee",
        amount=25.00,
        currency="ZMW"
    )
    db_session.add(fee)
    db_session.commit()

    assert fee.loan is not None
    assert fee.loan.id == loan.id