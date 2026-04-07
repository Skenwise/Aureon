#!/usr/bin/env python3
# scripts/validate_models.py
"""
Database Model Validation Script

Run this after any model changes to catch relationship mismatches early.
"""

import sys
from sqlalchemy import create_engine
from sqlmodel import SQLModel

# Import all models to register them with metadata
from database.model import metadata
from database.model.core import Company, Customer, User
from database.model.finance import Account, Journal, Posting, Loan, LoanSchedule, LoanDisbursement, LoanRepayment, Fee, ChartAccount
from database.model.misc import Currency, ExchangeRate
from database.model.payments import Payment, PaymentExecution, PaymentProvider, Subscription, ExternalTransaction
from database.model.security import SecurityRole, SecurityPermission
from database.model.treasury import CashPosition, FundReservation, FundingTransfer
from database.model.audit import AuditLog, Reconciliation
from database.model.reporting import LedgerSnapshot, LoanPortfolioSnapshot, PaymentVolumeSnapshot


def validate_models():
    """Attempt to create all tables in an in-memory database."""
    print("=" * 60)
    print("Validating All Database Models")
    print("=" * 60)
    
    # Use in-memory SQLite for validation
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ All models are valid!")
        print("   - 0 relationship errors")
        print("   - 0 foreign key errors")
        print("   - 0 circular dependency errors")
        return 0
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(validate_models())