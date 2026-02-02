#Middleware/DataProvider/AccountProvider/accountProvider.py

"""
Account data provider.

Provides database access for Account (ledger) model.
Supports deterministic retrieval, creation, update, and listing operations.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session, col
from database.model.finance.account import Account
from backend.core.error import NotFoundError, CalculationError


class AccountProvider:
    """
    Provider for ledger account queries and operations.

    Encapsulates all database logic for accounts. All operations
    are deterministic and validated before returning results.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session (Session): SQLModel session for DB operations.
        """
        self.session = session

    # ----------------- Account Operations ----------------- #

    def create_account(self, account: Account) -> Account:
        """
        Persist a new ledger account in the database.

        Args:
            account (Account): Account object to persist.

        Returns:
            Account: The created account with ID and timestamps.

        Raises:
            ValueError: If an account with the same account_number already exists.
        """
        stmt = select(Account).where(Account.account_number == account.account_number)
        existing = self.session.exec(stmt).first()
        if existing:
            raise ValueError(f"Account with number {account.account_number} already exists.")

        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_account(self, account_id: UUID) -> Account:
        """
        Retrieve a ledger account by its unique ID.

        Args:
            account_id (UUID): Ledger account identifier.

        Returns:
            Account: Ledger account object.

        Raises:
            NotFoundError: If no account exists with the given ID.
        """
        stmt = select(Account).where(Account.id == account_id)
        account = self.session.exec(stmt).first()
        if not account:
            raise NotFoundError("Account", str(account_id))
        return account

    def update_account(self, account_id: UUID, updated_fields: dict) -> Account:
        """
        Update an existing ledger account.

        Args:
            account_id (UUID): Ledger account identifier.
            updated_fields (dict): Fields to update (e.g., name, parent_account_id).

        Returns:
            Account: Updated account object.

        Raises:
            NotFoundError: If account does not exist.
        """
        account = self.get_account(account_id)
        for key, value in updated_fields.items():
            if hasattr(account, key):
                setattr(account, key, value)
        account.version += 1
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def list_accounts(self) -> List[Account]:
        """
        List all ledger accounts.

        Returns:
            List[Account]: All accounts in the ledger.
        """
        stmt = select(Account)
        return list(self.session.exec(stmt).all())
