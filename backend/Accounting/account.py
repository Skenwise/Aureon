#backend/Accounting/account.py

"""
Account Port & Adapter.

Defines core ledger account operations and delegates to AccountProvider.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.accountSchema import AccountCreate, AccountRead, AccountUpdate
from backend.core.error import NotFoundError
from Middleware.DataProvider.AccountProvider.accountProvider import AccountProvider


class AccountPort(Protocol):
    """
    Port interface for ledger account operations.

    All operations are deterministic, validated, and raise domain errors
    when necessary. No provider or infra logic should be handled here.
    """

    def create_account(self, account_in: AccountCreate) -> AccountRead:
        """
        Create a new ledger account.

        Args:
            account_in (AccountCreate): Input data for the new account.

        Returns:
            AccountRead: The created ledger account.

        Raises:
            ValueError: If an account with the same code already exists.
        """
        raise NotImplementedError

    def get_account(self, account_id: UUID) -> AccountRead:
        """
        Retrieve an account by its unique ID.

        Args:
            account_id (UUID): Ledger account identifier.

        Returns:
            AccountRead: Ledger account information.

        Raises:
            NotFoundError: If the account does not exist.
        """
        raise NotImplementedError

    def update_account(self, account_id: UUID, account_in: AccountUpdate) -> AccountRead:
        """
        Update an existing ledger account.

        Only provided fields will be updated.

        Args:
            account_id (UUID): Ledger account identifier.
            account_in (AccountUpdate): Fields to update.

        Returns:
            AccountRead: Updated ledger account.

        Raises:
            NotFoundError: If the account does not exist.
        """
        raise NotImplementedError

    def list_accounts(self) -> List[AccountRead]:
        """
        List all ledger accounts.

        Returns:
            List[AccountRead]: All accounts in the ledger.
        """
        raise NotImplementedError
    
class AccountAdapter(AccountPort):
    """
    Adapter implementation of AccountPort.

    Delegates all ledger account operations to AccountProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: AccountProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (AccountProvider): The data provider for account operations.
        """
        self.provider = provider

    def create_account(self, account_in: AccountCreate) -> AccountRead:
        """
        Create a new ledger account via the provider.
        """
        account_model = self.provider.create_account(cast(Any, account_in))
        return AccountRead.model_validate(account_model)

    def get_account(self, account_id: UUID) -> AccountRead:
        """
        Retrieve an account by ID via the provider.
        """
        account_model = self.provider.get_account(account_id)
        return AccountRead.model_validate(account_model)

    def update_account(self, account_id: UUID, account_in: AccountUpdate) -> AccountRead:
        """
        Update an existing account via the provider.
        """
        updated_fields = account_in.model_dump(exclude_unset=True)
        account_model = self.provider.update_account(account_id, updated_fields)
        return AccountRead.model_validate(account_model)

    def list_accounts(self) -> List[AccountRead]:
        """
        List all ledger accounts via the provider.
        """
        accounts = self.provider.list_accounts()
        return [AccountRead.model_validate(a) for a in accounts]
