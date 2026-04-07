# tests/db/test_loan_model.py
"""Integration tests for Loan model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.loan import Loan


def test_create_loan(db_session):
    """Create a valid Loan record and verify it persists correctly."""
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="LOANCO", name="Loan Company")
    customer = Customer(first_name="Borrower", last_name="One", company_id=company.id)
    
    db_session.add_all([currency, company, customer])
    db_session.commit()

    start_date = date.today()
    end_date = start_date + timedelta(days=365)

    loan = Loan(
        customer_id=customer.id,
        loan_number="LN-001",
        principal_amount=10000.00,
        interest_rate=12.5,
        start_date=start_date,
        end_date=end_date,
        term_months=12,
        status="active",
        currency="USD"
    )
    db_session.add(loan)
    db_session.commit()

    retrieved = db_session.get(Loan, loan.id)
    assert retrieved is not None
    assert retrieved.loan_number == "LN-001"
    assert retrieved.principal_amount == 10000.00
    assert retrieved.interest_rate == 12.5


def test_loan_unique_constraints(db_session):
    """Duplicate loan_number should raise IntegrityError."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="UNIQLN", name="Unique Loan Co")
    customer = Customer(first_name="Test", last_name="User", company_id=company.id)
    
    db_session.add_all([currency, company, customer])
    db_session.commit()

    loan1 = Loan(
        customer_id=customer.id,
        loan_number="UNIQ001",
        principal_amount=1000,
        interest_rate=10,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )
    loan2 = Loan(
        customer_id=customer.id,
        loan_number="UNIQ001",
        principal_amount=2000,
        interest_rate=15,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )

    db_session.add(loan1)
    db_session.commit()

    db_session.add(loan2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_loan_relationships(db_session):
    """Test Loan to Customer and Company relationships."""
    currency = Currency(code="EUR", name="Euro", decimals=2)
    company = Company(code="RELLOAN", name="Relationship Loan Co")
    customer = Customer(first_name="Rel", last_name="Borrower", company_id=company.id)
    
    db_session.add_all([currency, company, customer])
    db_session.commit()

    loan = Loan(
        customer_id=customer.id,
        loan_number="REL-001",
        principal_amount=5000,
        interest_rate=8,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="EUR",
        company_id=company.id  # ← Added
    )
    db_session.add(loan)
    db_session.commit()

    assert loan.customer is not None
    assert loan.customer.id == customer.id
    assert loan.company is not None
    assert loan.company.id == company.id