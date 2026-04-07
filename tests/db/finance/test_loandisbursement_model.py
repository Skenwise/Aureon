# tests/db/test_loandisbursement_model.py
"""Integration tests for LoanDisbursement model using isolated database harness."""

from datetime import date, timedelta

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.account import Account
from database.model.finance.loan import Loan
from database.model.finance.loan_disbursement import LoanDisbursement


def test_create_loan_disbursement(db_session):
    """Create a valid LoanDisbursement record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="DISBCO", name="Disbursement Company")
    customer = Customer(first_name="Disburse", last_name="Customer", company_id=company.id)
    account = Account(account_number="DISB-ACC", account_type="ASSET", currency="USD")
    loan = Loan(
        customer_id=customer.id,
        loan_number="DISB-001",
        principal_amount=10000,
        interest_rate=12,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="USD"
    )
    
    db_session.add_all([currency, company, customer, account, loan])
    db_session.commit()

    disbursement = LoanDisbursement(
        loan_id=loan.id,
        disbursement_amount=10000.00,
        disbursement_account_id=account.id,
        disbursement_date=date.today(),
        payment_provider="INTERNAL",
        status="COMPLETED",
        reference="DISB-REF-001"
    )
    db_session.add(disbursement)
    db_session.commit()

    retrieved = db_session.get(LoanDisbursement, disbursement.id)
    assert retrieved is not None
    assert retrieved.disbursement_amount == 10000.00
    assert retrieved.payment_provider == "INTERNAL"


def test_loan_disbursement_relationships(db_session):
    """Test LoanDisbursement to Loan and Account relationships."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELDIS", name="Relationship Disbursement Co")
    customer = Customer(first_name="Rel", last_name="Disburse", company_id=company.id)
    account = Account(account_number="RELDIS-ACC", account_type="ASSET", currency="ZMW")
    loan = Loan(
        customer_id=customer.id,
        loan_number="RELDIS-001",
        principal_amount=5000,
        interest_rate=10,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="ZMW"
    )
    
    db_session.add_all([currency, company, customer, account, loan])
    db_session.commit()

    disbursement = LoanDisbursement(
        loan_id=loan.id,
        disbursement_amount=5000,
        disbursement_account_id=account.id,
        disbursement_date=date.today(),
        payment_provider="BANK"
    )
    db_session.add(disbursement)
    db_session.commit()

    assert disbursement.loan is not None
    assert disbursement.loan.id == loan.id
    assert disbursement.disbursement_account is not None
    assert disbursement.disbursement_account.id == account.id