"""
Account data provider.

Provides database access for Account (ledger) model.
Supports deterministic retrieval, creation, update, and listing operations.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, col
from database.model.finance.account import Account
from backend.core.error import NotFoundError, CalculationError


class AccountProvider:
    """
    Provider for ledger account queries and operations.

    Encapsulates all database logic for accounts. All operations
    are deterministic and validated before returning results.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for DB operations.
        """
        self.session = session

    # ----------------- Account Operations ----------------- #

    async def create_account(self, account: Account) -> Account:
        """
        Persist a new ledger account in the database.

        Args:
            account (Account): Account object to persist.

        Returns:
            Account: The created account with ID and timestamps.

        Raises:
            ValueError: If an account with the same account_number already exists.
        """
        stmt = select(Account).where(Account.account_number == account.account_number)  # type: ignore
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Account with number {account.account_number} already exists.")

        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_account(self, account_id: UUID) -> Account:
        """
        Retrieve a ledger account by its unique ID.

        Args:
            account_id (UUID): Ledger account identifier.

        Returns:
            Account: Ledger account object.

        Raises:
            NotFoundError: If no account exists with the given ID.
        """
        stmt = select(Account).where(Account.id == account_id)  # type: ignore
        result = await self.session.execute(stmt)
        account = result.scalar_one_or_none()
        if not account:
            raise NotFoundError("Account", str(account_id))
        return account

    async def update_account(self, account_id: UUID, updated_fields: dict) -> Account:
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
        account = await self.get_account(account_id)
        for key, value in updated_fields.items():
            if hasattr(account, key):
                setattr(account, key, value)
        account.version += 1
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def list_accounts(self) -> List[Account]:
        """
        List all ledger accounts.

        Returns:
            List[Account]: All accounts in the ledger.
        """
        stmt = select(Account)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
