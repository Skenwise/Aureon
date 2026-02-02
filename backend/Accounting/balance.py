# backend/Accounting/balance.py

"""
Balance computation module.

Provides read-only, bank-grade ledger balance calculations
including:

- Single account balances
- Period balances
- Trial balances

All computations are immutable, deterministic, and audit-ready.
Interacts with Postings and Journals via Providers, and uses
the Money value object for currency-aware arithmetic.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

# Core value object for currency-aware arithmetic
from backend.core.money import Money

# Errors
from backend.core.error import CalculationError, ValidationError

# Schemas (inline or from balanceSchema)
from pydantic import BaseModel, Field

from Accounting.account import AccountAdapter
from Accounting.posting import Posting
from Accounting.journal import JournalAdapter
from Accounting.chart_of_accounts import ChartAccountAdapter

from schemas.balanceSchema import AccountBalanceRead, PeriodBalanceRead, TrialBalanceRead, TrialBalanceItem
from schemas.journalSchema import JournalRead

class AccountBalance:
    """
    Computes balances for a single ledger account.
    Responsibilities:
        - Aggregate debit and credit postings
        - Ensure currency consistency
        - Return a currency-aware balance object
    """
    def __init__(self, account_adapter: AccountAdapter, journal_adapter: JournalAdapter):
        """
        Initialize the account balance computation service.
        Args:
            account_adapter: Adapter for ledger account retrieval.
            journal_adapter: Adapter for journal retrieval.
        """
        self.account_adapter = account_adapter
        self.journal_adapter = journal_adapter
    def compute(self, account_id: UUID, currency: Optional[str] = None) -> AccountBalanceRead:
        """
        Compute the current balance for the specified account.
        Args:
            account_id: The ledger account ID.
            currency: If provided, enforce currency filter.
        Returns:
            AccountBalanceRead: Immutable balance snapshot for the account.
        Raises:
            ValidationError: If account is not found or currency mismatch occurs.
            CalculationError: If arithmetic fails.
        """
        # Retrieve account metadata
        account = self.account_adapter.get_account(account_id)
        if currency and account.currency_code != currency:
            raise ValidationError(f"Currency mismatch: account is {account.currency_code}, requested {currency}")
        balance = Money(amount=Decimal(0), currency=account.currency_code)
        last_updated: Optional[datetime] = None
        # Iterate over all journals (assuming list_journals returns processed only)
        journals: List[JournalRead] = self.journal_adapter.list_journals()
        for journal in journals:
            for posting in getattr(journal, "postings", []):
                if posting.debit_account_id == account_id:
                    balance += posting.money
                elif posting.credit_account_id == account_id:
                    balance -= posting.money
                last_updated = max(last_updated, getattr(posting, "timestamp", datetime.utcnow())) if last_updated else getattr(posting, "timestamp", datetime.utcnow())
        return AccountBalanceRead(
            account_id=account.id,
            account_name=account.name,
            account_type=account.account_type,
            currency=account.currency_code,
            balance=balance.amount,
            last_updated=last_updated,
        )
    
class PeriodBalance:
    """Computes account balances over a specific date range.

    Responsibilities:
        - Calculate opening balance (before period start).
        - Aggregate debits and credits within the period.
        - Derive closing balance.
        - Ensure currency consistency throughout.
    """

    def __init__(self, account_adapter: AccountAdapter, journal_adapter: JournalAdapter):
        """Initialize the period balance computation service.

        Args:
            account_adapter (AccountAdapter): Adapter for ledger account retrieval.
            journal_adapter (JournalAdapter): Adapter for journal retrieval.
        """
        self.account_adapter = account_adapter
        self.journal_adapter = journal_adapter

    def compute(
        self,
        account_id: UUID,
        period_start: datetime,
        period_end: datetime,
        currency: Optional[str] = None,
    ) -> PeriodBalanceRead:
        """Compute the period balance for a specific account.

        Args:
            account_id (UUID): The ledger account ID.
            period_start (datetime): Start of the period (inclusive).
            period_end (datetime): End of the period (inclusive).
            currency (Optional[str]): If provided, enforce currency filter.

        Returns:
            PeriodBalanceRead: Immutable period balance snapshot.

        Raises:
            ValidationError: If dates are invalid or currency mismatch occurs.
            CalculationError: If arithmetic fails.
        """
        if period_start > period_end:
            raise ValidationError("period_start cannot be after period_end")

        account = self.account_adapter.get_account(account_id)

        if currency and account.currency_code != currency:
            raise ValidationError(
                f"Currency mismatch: account is {account.currency_code}, requested {currency}"
            )

        opening_balance: Money = Money(amount=Decimal(0), currency=account.currency_code)
        total_debit: Money = Money(amount=Decimal(0), currency=account.currency_code)
        total_credit: Money = Money(amount=Decimal(0), currency=account.currency_code)

        journals: List[JournalRead] = self.journal_adapter.list_journals()

        for journal in journals:
            for posting in getattr(journal, "postings", []):
                posting_date: Optional[datetime] = getattr(posting, "timestamp", None)

                if posting_date is None:
                    continue

                is_debit: bool = posting.debit_account_id == account_id
                is_credit: bool = posting.credit_account_id == account_id

                if not is_debit and not is_credit:
                    continue

                # Before period → contributes to opening balance
                if posting_date < period_start:
                    if is_debit:
                        opening_balance += posting.money
                    elif is_credit:
                        opening_balance -= posting.money

                # Within period → contributes to debits/credits
                elif period_start <= posting_date <= period_end:
                    if is_debit:
                        total_debit += posting.money
                    elif is_credit:
                        total_credit += posting.money

        closing_balance: Money = opening_balance + total_debit - total_credit

        return PeriodBalanceRead(
            account_id=account.id,
            account_name=account.name,
            account_type=account.account_type,
            currency=account.currency_code,
            period_start=period_start,
            period_end=period_end,
            opening_balance=opening_balance.amount,
            closing_balance=closing_balance.amount,
            total_debit=total_debit.amount,
            total_credit=total_credit.amount,
        )


class TrialBalance:
    """Generates trial balances across all or selected accounts.

    Responsibilities:
        - Aggregate per-account debit/credit totals.
        - Validate total debits equal total credits (double-entry check).
        - Return a full trial balance snapshot.
    """

    def __init__(
        self,
        account_adapter: AccountAdapter,
        journal_adapter: JournalAdapter,
        chart_account_adapter: ChartAccountAdapter,
    ):
        """Initialize the trial balance computation service.

        Args:
            account_adapter (AccountAdapter): Adapter for ledger account retrieval.
            journal_adapter (JournalAdapter): Adapter for journal retrieval.
            chart_account_adapter (ChartAccountAdapter): Adapter for chart of accounts retrieval.
        """
        self.account_adapter = account_adapter
        self.journal_adapter = journal_adapter
        self.chart_account_adapter = chart_account_adapter

    def compute(
        self,
        company_id: Optional[UUID] = None,
        account_ids: Optional[List[UUID]] = None,
        as_of: Optional[datetime] = None,
    ) -> TrialBalanceRead:
        """Generate a trial balance, optionally filtered by accounts or date.

        Args:
            company_id (Optional[UUID]): The company to generate the trial balance for.
            account_ids (Optional[List[UUID]]): If provided, only include these accounts.
                Otherwise all accounts are included.
            as_of (Optional[datetime]): If provided, only include postings up to this date.

        Returns:
            TrialBalanceRead: Full trial balance with per-account and aggregate totals.

        Raises:
            ValidationError: If no accounts are found.
            CalculationError: If total debits and credits don't balance.
        """
        # Fetch all accounts from chart of accounts
        all_accounts: List[Any] = self.chart_account_adapter.list_chart_accounts()

        if not all_accounts:
            raise ValidationError("No accounts found in chart of accounts")

        # Filter by account_ids if provided
        accounts: List[Any] = (
            [a for a in all_accounts if a.id in account_ids]
            if account_ids
            else all_accounts
        )

        if not accounts:
            raise ValidationError("None of the provided account_ids exist")

        # Determine currency from first account
        currency: str = accounts[0].currency_code

        # Build a map: account_id → { debit: Money, credit: Money }
        account_totals: Dict[UUID, Dict[str, Money]] = {}

        for account in accounts:
            account_totals[account.id] = {
                "debit": Money(amount=Decimal(0), currency=account.currency_code),
                "credit": Money(amount=Decimal(0), currency=account.currency_code),
            }

        # Iterate journals and aggregate postings
        journals: List[JournalRead] = self.journal_adapter.list_journals()

        for journal in journals:
            for posting in getattr(journal, "postings", []):
                posting_date: Optional[datetime] = getattr(posting, "timestamp", None)

                # If as_of filter is set, skip postings after that date
                if as_of and posting_date and posting_date > as_of:
                    continue

                debit_id: UUID = posting.debit_account_id
                credit_id: UUID = posting.credit_account_id

                if debit_id in account_totals:
                    account_totals[debit_id]["debit"] += posting.money

                if credit_id in account_totals:
                    account_totals[credit_id]["credit"] += posting.money

        # Build per-account trial balance items
        items: List[TrialBalanceItem] = []
        grand_total_debit: Money = Money(amount=Decimal(0), currency=currency)
        grand_total_credit: Money = Money(amount=Decimal(0), currency=currency)

        for account in accounts:
            totals: Dict[str, Money] = account_totals[account.id]

            items.append(TrialBalanceItem(
                account_id=account.id,
                account_name=account.name,
                account_type=account.account_type,
                currency=account.currency_code,
                debit=totals["debit"].amount,
                credit=totals["credit"].amount,
            ))

            grand_total_debit += totals["debit"]
            grand_total_credit += totals["credit"]

        # Double-entry integrity check
        if grand_total_debit.amount != grand_total_credit.amount:
            raise CalculationError(
                f"Trial balance does not balance: "
                f"total debit={grand_total_debit.amount}, "
                f"total credit={grand_total_credit.amount}"
            )

        generated_at: datetime = datetime.utcnow()

        return TrialBalanceRead(
            company_id=company_id,
            currency=currency,
            items=items,
            total_debit=grand_total_debit.amount,
            total_credit=grand_total_credit.amount,
            generated_at=generated_at,
        )
