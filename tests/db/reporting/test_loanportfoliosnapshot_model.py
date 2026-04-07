# tests/db/reporting/test_loanportfoliosnapshot_model.py
"""Integration tests for LoanPortfolioSnapshot model using isolated database harness."""

from datetime import date, timedelta
from decimal import Decimal

from database.model.core.company import Company
from database.model.core.customer import Customer
from database.model.misc.currency import Currency
from database.model.finance.loan import Loan
from database.model.reporting.loan_portofolio import LoanPortfolioSnapshot


def test_create_loan_portfolio_snapshot(db_session):
    """Create a valid LoanPortfolioSnapshot record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="LOANPORTCO", name="Loan Portfolio Company")
    customer = Customer(first_name="Port", last_name="Folio", company_id=company.id)
    loan = Loan(
        customer_id=customer.id,
        loan_number="PORT-001",
        principal_amount=10000,
        interest_rate=12,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        term_months=12,
        currency="USD",
        company_id=company.id
    )
    
    db_session.add_all([currency, company, customer, loan])
    db_session.commit()

    snapshot = LoanPortfolioSnapshot(
        tenant_id=company.id,
        snapshot_date=date.today(),
        loan_id=loan.id,
        loan_number="PORT-001",
        principal_amount=Decimal("10000.00"),
        outstanding_balance=Decimal("8500.00"),
        overdue_days=0,
        status="ACTIVE"
    )
    db_session.add(snapshot)
    db_session.commit()

    retrieved = db_session.get(LoanPortfolioSnapshot, snapshot.id)
    assert retrieved is not None
    assert retrieved.loan_number == "PORT-001"
    assert retrieved.principal_amount == Decimal("10000.00")
    assert retrieved.status == "ACTIVE"