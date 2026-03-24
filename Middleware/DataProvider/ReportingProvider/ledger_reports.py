#Middleware/DataProvider/ReportingProvider/ledger_reports.py

"""
Ledger Reports Provider.

Provides read-only aggregation of account and journal data for reporting.
Uses AccountProvider and JournalProvider for source data.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlmodel import Session

from Middleware.DataProvider.AccountProvider.accountProvider import AccountProvider
from Middleware.DataProvider.AccountProvider.journalProvider import JournalProvider
from schemas.reportingSchema import (
    AccountBalanceReport,
    TrialBalanceReport,
    BalanceSheetReport,
    IncomeStatementReport
)


class LedgerReportsProvider:
    """
    Provider for ledger-related reports.
    """

    def __init__(self, session: Session):
        self.session = session
        self.account_provider = AccountProvider(session)
        self.journal_provider = JournalProvider(session)

    def get_account_balance(
        self, 
        account_id: UUID, 
        as_of_date: date
    ) -> AccountBalanceReport:
        """Get account balance as of a specific date."""
        account = self.account_provider.get_account(account_id)
        
        balance = Decimal(str(account.balance)) if hasattr(account, 'balance') else Decimal("0")
        
        return AccountBalanceReport(
            account_id=account.id,
            account_code=account.account_number,
            account_name=account.account_number,  # No name field, use account_number
            account_type=account.account_type,
            currency=account.currency,
            balance=balance,
            debit_count=0,
            credit_count=0,
            last_activity=None
        )

    def get_trial_balance(
        self, 
        company_id: UUID,
        as_of_date: date
    ) -> TrialBalanceReport:
        """Get trial balance (all accounts with balances)."""
        accounts = self.account_provider.list_accounts()
        
        account_balances = []
        for account in accounts:
            # Filter by company_id for multi-tenancy
            if account.company_id != company_id:
                continue
                
            balance = Decimal(str(account.balance)) if hasattr(account, 'balance') else Decimal("0")
            
            account_balances.append(
                AccountBalanceReport(
                    account_id=account.id,
                    account_code=account.account_number,
                    account_name=account.account_number,
                    account_type=account.account_type,
                    currency=account.currency,
                    balance=balance,
                    debit_count=0,
                    credit_count=0,
                    last_activity=None
                )
            )
        
        return TrialBalanceReport(
            as_of_date=as_of_date,
            tenant_id=company_id,  # Response uses tenant_id for consistency
            accounts=account_balances
        )

    def get_balance_sheet(
        self, 
        company_id: UUID,
        as_of_date: date
    ) -> BalanceSheetReport:
        """Get balance sheet (Assets = Liabilities + Equity)."""
        accounts = self.account_provider.list_accounts()
        
        assets = []
        liabilities = []
        equity = []
        
        for account in accounts:
            if account.company_id != company_id:
                continue
                
            balance = Decimal(str(account.balance)) if hasattr(account, 'balance') else Decimal("0")
            
            report = AccountBalanceReport(
                account_id=account.id,
                account_code=account.account_number,
                account_name=account.account_number,
                account_type=account.account_type,
                currency=account.currency,
                balance=balance,
                debit_count=0,
                credit_count=0,
                last_activity=None
            )
            
            account_type = account.account_type.upper() if account.account_type else ""
            
            if account_type in ["ASSET", "CASH", "BANK", "LOAN_RECEIVABLE", "RECEIVABLE"]:
                assets.append(report)
            elif account_type in ["LIABILITY", "DEPOSIT", "LOAN_PAYABLE", "PAYABLE"]:
                liabilities.append(report)
            elif account_type in ["EQUITY", "CAPITAL", "RETAINED_EARNINGS"]:
                equity.append(report)
        
        return BalanceSheetReport(
            as_of_date=as_of_date,
            tenant_id=company_id,
            assets=assets,
            liabilities=liabilities,
            equity=equity
        )

    def get_income_statement(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> IncomeStatementReport:
        """Get income statement (Revenue - Expenses = Net Income)."""
        accounts = self.account_provider.list_accounts()
        
        revenue = []
        expenses = []
        
        for account in accounts:
            if account.company_id != company_id:
                continue
                
            balance = Decimal(str(account.balance)) if hasattr(account, 'balance') else Decimal("0")
            
            report = AccountBalanceReport(
                account_id=account.id,
                account_code=account.account_number,
                account_name=account.account_number,
                account_type=account.account_type,
                currency=account.currency,
                balance=balance,
                debit_count=0,
                credit_count=0,
                last_activity=None
            )
            
            account_type = account.account_type.upper() if account.account_type else ""
            
            if account_type in ["INCOME", "REVENUE", "INTEREST_INCOME", "FEE_INCOME", "SERVICE_INCOME"]:
                revenue.append(report)
            elif account_type in ["EXPENSE", "INTEREST_EXPENSE", "OPERATING_EXPENSE", "ADMIN_EXPENSE"]:
                expenses.append(report)
        
        return IncomeStatementReport(
            start_date=start_date,
            end_date=end_date,
            tenant_id=company_id,
            revenue=revenue,
            expenses=expenses
        )