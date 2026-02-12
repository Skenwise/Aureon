#Middleware/DataProvider/treasuryProvider/FundingProvider.py

"""
Funding Data Provider.

Handles persistence and lifecycle management of funding transfers between provider accounts.

This provider strictly performs database operations and state transitions.
No external provider API logic is implemented here.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, or_
from uuid import UUID

from database.model.treasury.funding_transfer import FundingTransfer
from database.model.treasury.cash_position import CashPosition

from backend.core.error import NotFoundError, ValidationError


class FundingProvider:
    """
    Data provider for FundingTransfer persistence and lifecycle management.

    Handles:

    - Transfer creation
    - Transfer retrieval
    - Transfer listing
    - Transfer state transitions
    """

    def __init__(self, session: Session):
        """
        Initialize provider with database session.

        Args:
            session (Session): Active SQLModel session.
        """
        self.session = session

    # ------------------------------------------------------------
    # Create
    # ------------------------------------------------------------

    def create_transfer(self, transfer_in) -> FundingTransfer:
        """
        Create a new funding transfer record.

        Does NOT execute external movement.
        Only records intent.

        Args:
            transfer_in: Transfer creation object.

        Returns:
            FundingTransfer: Created transfer model.

        Raises:
            ValidationError: If source position does not exist or insufficient funds.
        """

        source = self._get_cash_position(
            transfer_in.from_provider,
            transfer_in.from_account_id
        )

        if source.currency_code != transfer_in.currency_code:
            raise ValidationError("Currency mismatch with source account")

        if source.available_balance < transfer_in.amount:
            raise ValidationError("Insufficient funds")

        transfer = FundingTransfer(
            transfer_id=transfer_in.transfer_id,
            from_provider=transfer_in.from_provider,
            from_account_id=transfer_in.from_account_id,
            to_provider=transfer_in.to_provider,
            to_account_id=transfer_in.to_account_id,
            amount=transfer_in.amount,
            currency_code=transfer_in.currency_code,
            status="PENDING",
            reference=transfer_in.reference,
            notes=transfer_in.notes
        )

        self.session.add(transfer)
        self.session.commit()
        self.session.refresh(transfer)

        return transfer

    # ------------------------------------------------------------
    # Read
    # ------------------------------------------------------------

    def get_transfer(self, transfer_id: str) -> FundingTransfer:
        """
        Retrieve transfer by ID.
        """

        statement = select(FundingTransfer).where(
            FundingTransfer.transfer_id == transfer_id
        )

        transfer = self.session.exec(statement).first()

        if not transfer:
            raise NotFoundError("FundingTransfer", f"ID: {transfer_id}")

        return transfer

    def list_transfers(
        self,
        provider: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[FundingTransfer]:
        """
        List transfers with optional filters.
        """

        statement = select(FundingTransfer)

        if provider:
            statement = statement.where(
                or_(
                    FundingTransfer.from_provider == provider,
                    FundingTransfer.to_provider == provider
                )
            )

        if status:
            statement = statement.where(
                FundingTransfer.status == status
            )

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------

    def complete_transfer(self, transfer_id: str) -> FundingTransfer:
        """
        Mark transfer completed and update liquidity positions.
        """

        transfer = self.get_transfer(transfer_id)

        if transfer.status != "PENDING":
            raise ValidationError("Only PENDING transfers can be completed")

        source = self._get_cash_position(
            transfer.from_provider,
            transfer.from_account_id
        )

        destination = self._get_cash_position(
            transfer.to_provider,
            transfer.to_account_id
        )

        # deduct from source
        source.total_balance -= transfer.amount
        source.available_balance -= transfer.amount

        # add to destination
        destination.total_balance += transfer.amount
        destination.available_balance += transfer.amount

        transfer.status = "COMPLETED"
        transfer.completed_at = datetime.utcnow()

        self.session.add(source)
        self.session.add(destination)
        self.session.add(transfer)

        self.session.commit()
        self.session.refresh(transfer)

        return transfer

    def fail_transfer(self, transfer_id: str, reason: str) -> FundingTransfer:
        """
        Mark transfer failed.
        """

        transfer = self.get_transfer(transfer_id)

        transfer.status = "FAILED"
        transfer.notes = reason
        transfer.completed_at = datetime.utcnow()

        self.session.add(transfer)
        self.session.commit()
        self.session.refresh(transfer)

        return transfer

    def cancel_transfer(self, transfer_id: str) -> FundingTransfer:
        """
        Cancel pending transfer.
        """

        transfer = self.get_transfer(transfer_id)

        if transfer.status != "PENDING":
            raise ValidationError("Only PENDING transfers can be cancelled")

        transfer.status = "CANCELLED"
        transfer.completed_at = datetime.utcnow()

        self.session.add(transfer)
        self.session.commit()
        self.session.refresh(transfer)

        return transfer

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _get_cash_position(
        self,
        provider: str,
        account_id: str
    ) -> CashPosition:
        """
        Retrieve cash position or fail.
        """

        statement = select(CashPosition).where(
            CashPosition.provider == provider,
            CashPosition.account_id == account_id
        )

        position = self.session.exec(statement).first()

        if not position:
            raise ValidationError(
                f"Cash position not found: {provider}/{account_id}"
            )

        return position
