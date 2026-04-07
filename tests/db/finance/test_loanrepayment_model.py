# tests/db/test_loanrepayment_model.py
"""Integration tests for LoanRepayment model using isolated database harness."""

from datetime import date, timedelta

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.loan import Loan
from database.model.finance.loan_repayment import LoanRepayment


def test_create_loan_repayment(db_session):
    """Create a valid LoanRepayment record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="REPAYCO", name="Repayment Company")
    customer = Customer(first_name="Repay", last_name="Customer", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="REPAY-001",
        principal_amount=10000,
        interest_rate=12,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="USD"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    repayment = LoanRepayment(
        loan_id=loan.id,
        payment_amount=1000.00,
        principal_applied=800.00,
        interest_applied=200.00,
        payment_date=date.today(),
        payment_method="MOBILE_MONEY",
        payment_provider="MTN",
        status="APPLIED",
        reference="REPAY-REF-001"
    )
    db_session.add(repayment)
    db_session.commit()

    retrieved = db_session.get(LoanRepayment, repayment.id)
    assert retrieved is not None
    assert retrieved.payment_amount == 1000.00
    assert retrieved.principal_applied == 800.00
    assert retrieved.interest_applied == 200.00


def test_loan_repayment_relationships(db_session):
    """Test LoanRepayment to Loan relationship."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELREP", name="Relationship Repayment Co")
    customer = Customer(first_name="Rel", last_name="Repay", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="RELREP-001",
        principal_amount=5000,
        interest_rate=10,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    repayment = LoanRepayment(
        loan_id=loan.id,
        payment_amount=500,
        principal_applied=400,
        interest_applied=100,
        payment_date=date.today(),
        payment_method="CASH"
    )
    db_session.add(repayment)
    db_session.commit()

    assert repayment.loan is not None
    assert repayment.loan.id == loan.id
    assert repayment.loan.loan_number == "RELREP-001"