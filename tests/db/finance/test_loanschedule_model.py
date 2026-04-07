# tests/db/test_loanschedule_model.py
"""Integration tests for LoanSchedule model using isolated database harness."""

from datetime import date, timedelta

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.loan import Loan
from database.model.finance.loan_schedule import LoanSchedule


def test_create_loan_schedule(db_session):
    """Create a valid LoanSchedule record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="SCHEDCO", name="Schedule Company")
    customer = Customer(first_name="Schedule", last_name="Customer", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="SCHED-001",
        principal_amount=10000,
        interest_rate=12,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="USD"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    schedule = LoanSchedule(
        loan_id=loan.id,
        installment_number=1,
        due_date=date.today() + timedelta(days=30),
        principal_due=833.33,
        interest_due=100.00,
        total_due=933.33,
        status="pending"
    )
    db_session.add(schedule)
    db_session.commit()

    retrieved = db_session.get(LoanSchedule, schedule.id)
    assert retrieved is not None
    assert retrieved.installment_number == 1
    assert retrieved.total_due == 933.33


def test_loan_schedule_relationships(db_session):
    """Test LoanSchedule to Loan relationship."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELSCH", name="Relationship Schedule Co")
    customer = Customer(first_name="Rel", last_name="Schedule", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="RELSCH-001",
        principal_amount=5000,
        interest_rate=10,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    schedule = LoanSchedule(
        loan_id=loan.id,
        installment_number=1,
        due_date=date.today() + timedelta(days=30),
        principal_due=416.67,
        interest_due=41.67,
        total_due=458.34
    )
    db_session.add(schedule)
    db_session.commit()

    assert schedule.loan is not None
    assert schedule.loan.id == loan.id
    assert schedule.loan.loan_number == "RELSCH-001"