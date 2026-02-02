#Middleware/DataProvider/AccountProvider/chartOfAccountProvider.py

"""
Chart Account data provider.

Handles all database operations for chart-of-accounts entries.
Ensures deterministic retrieval, uniqueness, and hierarchy validation.
"""

from sqlmodel import Session, select, col
from uuid import UUID, uuid4
from datetime import datetime
from backend.core.error import NotFoundError, ValidationError
from database.model.finance.chart_of_account import ChartAccount
from schemas.chartOfAccountsSchema import ChartAccountCreate, ChartAccountUpdate

class ChartAccountProvider:
    """
    Provider for chart-of-accounts operations.
    Encapsulates all DB logic and enforces deterministic validation rules.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session (Session): SQLModel session for DB operations.
        """
        self.session = session

    # ----------------- Create ----------------- #
    def create_chart_account(self, account_in: ChartAccountCreate) -> ChartAccount:
        """
        Create a new chart-of-accounts entry.

        Args:
            account_in (ChartAccountCreate): Input data for the new chart account.

        Returns:
            ChartAccount: Created DB model.

        Raises:
            ValidationError: If an account with the same code already exists.
        """
        stmt = select(ChartAccount).where(ChartAccount.code == account_in.code.upper())
        existing = self.session.exec(stmt).first()
        if existing:
            raise ValidationError(f"Chart account with code '{account_in.code}' already exists.")

        # Validate parent exists if provided
        if account_in.parent_account_id:
            parent = self.session.get(ChartAccount, account_in.parent_account_id)
            if not parent:
                raise ValidationError(f"Parent chart account {account_in.parent_account_id} does not exist.")

        new_account = ChartAccount(
            id=uuid4(),
            code=account_in.code.upper(),
            name=account_in.name,
            account_type=account_in.account_type.upper(),
            parent_account_id=account_in.parent_account_id,
            description=account_in.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            version=1,
        )

        self.session.add(new_account)
        self.session.commit()
        self.session.refresh(new_account)
        return new_account

    # ----------------- Read ----------------- #
    def get_chart_account(self, account_id: UUID) -> ChartAccount:
        """
        Retrieve a chart-of-accounts entry by ID.

        Args:
            account_id (UUID): Chart account ID.

        Returns:
            ChartAccount: DB model.

        Raises:
            NotFoundError: If the chart account does not exist.
        """
        account = self.session.get(ChartAccount, account_id)
        if not account:
            raise NotFoundError("ChartAccount", str(account_id))
        return account

    # ----------------- Update ----------------- #
    def update_chart_account(self, account_id: UUID, updates: dict) -> ChartAccount:
        """
        Update an existing chart-of-accounts entry.

        Args:
            account_id (UUID): Chart account ID.
            updates (dict): Fields to update.

        Returns:
            ChartAccount: Updated DB model.

        Raises:
            NotFoundError: If the chart account does not exist.
            ValidationError: If parent account is invalid.
        """
        account = self.session.get(ChartAccount, account_id)
        if not account:
            raise NotFoundError("ChartAccount", str(account_id))

        # Validate parent if updating
        parent_id = updates.get("parent_account_id")
        if parent_id:
            parent = self.session.get(ChartAccount, parent_id)
            if not parent:
                raise ValidationError(f"Parent chart account {parent_id} does not exist.")

        for key, value in updates.items():
            if hasattr(account, key):
                setattr(account, key, value)

        account.updated_at = datetime.utcnow()
        account.version += 1

        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    # ----------------- List ----------------- #
    def list_chart_accounts(self) -> list[ChartAccount]:
        """
        List all chart-of-accounts entries.

        Returns:
            List[ChartAccount]: All chart accounts in the system.
        """
        stmt = select(ChartAccount).order_by(col(ChartAccount.code))
        return list(self.session.exec(stmt).all())
