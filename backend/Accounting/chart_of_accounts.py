# backend/Accounting/chart_of_accounts.py

"""
Chart of Accounts Port & Adapter.

Defines chart-of-accounts operations and delegates to ChartAccountProvider.
"""

from typing import List, Protocol
from uuid import UUID
from schemas.chartOfAccountsSchema import ChartAccountCreate, ChartAccountRead, ChartAccountUpdate
from backend.core.error import NotFoundError
from Middleware.DataProvider.AccountProvider.chartOfAccountProvider import ChartAccountProvider


class ChartAccountPort(Protocol):
    """
    Port interface for chart-of-accounts operations.

    All operations are deterministic, validated, and raise domain errors
    when necessary. No provider or infra logic should be handled here.
    """

    def create_chart_account(self, account_in: ChartAccountCreate) -> ChartAccountRead:
        """
        Create a new chart-of-accounts entry.

        Args:
            account_in (ChartAccountCreate): Input data for the new chart account.

        Returns:
            ChartAccountRead: The created chart-of-accounts entry.

        Raises:
            ValueError: If an account with the same code already exists.
        """
        raise NotImplementedError

    def get_chart_account(self, account_id: UUID) -> ChartAccountRead:
        """
        Retrieve a chart account by its unique ID.

        Args:
            account_id (UUID): Chart account identifier.

        Returns:
            ChartAccountRead: Chart-of-accounts entry information.

        Raises:
            NotFoundError: If the account does not exist.
        """
        raise NotImplementedError

    def update_chart_account(self, account_id: UUID, account_in: ChartAccountUpdate) -> ChartAccountRead:
        """
        Update an existing chart-of-accounts entry.

        Only provided fields will be updated.

        Args:
            account_id (UUID): Chart account identifier.
            account_in (ChartAccountUpdate): Fields to update.

        Returns:
            ChartAccountRead: Updated chart account.

        Raises:
            NotFoundError: If the account does not exist.
        """
        raise NotImplementedError

    def list_chart_accounts(self) -> List[ChartAccountRead]:
        """
        List all chart-of-accounts entries.

        Returns:
            List[ChartAccountRead]: All chart accounts in the ledger.
        """
        raise NotImplementedError


# ---------------------- Adapter ---------------------- #

class ChartAccountAdapter(ChartAccountPort):
    """
    Adapter implementation of ChartAccountPort.

    Delegates all chart-of-accounts operations to ChartAccountProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: ChartAccountProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (ChartAccountProvider): The data provider for chart accounts.
        """
        self.provider = provider

    def create_chart_account(self, account_in: ChartAccountCreate) -> ChartAccountRead:
        """
        Create a new chart-of-accounts entry via the provider.
        """
        account_model = self.provider.create_chart_account(account_in)
        return ChartAccountRead.from_orm(account_model)

    def get_chart_account(self, account_id: UUID) -> ChartAccountRead:
        """
        Retrieve a chart account by ID via the provider.
        """
        account_model = self.provider.get_chart_account(account_id)
        return ChartAccountRead.from_orm(account_model)

    def update_chart_account(self, account_id: UUID, account_in: ChartAccountUpdate) -> ChartAccountRead:
        """
        Update an existing chart account via the provider.
        """
        updated_fields = account_in.dict(exclude_unset=True)
        account_model = self.provider.update_chart_account(account_id, updated_fields)
        return ChartAccountRead.from_orm(account_model)

    def list_chart_accounts(self) -> List[ChartAccountRead]:
        """
        List all chart-of-accounts entries via the provider.
        """
        accounts = self.provider.list_chart_accounts()
        return [ChartAccountRead.from_orm(a) for a in accounts]
