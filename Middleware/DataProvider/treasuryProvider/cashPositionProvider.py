#Middleware/DataProvider/treasuryProvider/cashPositionProvider.py

"""
Cash Position Data Provider.

Handles persistence and retrieval of CashPosition records.

This provider is the authoritative storage layer for provider account balances.
It does NOT execute reservations or funding transfers.
It only manages the state of CashPosition.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from database.model.treasury.cash_position import CashPosition
from schemas.treasurySchema import ReserveFundsCreate

from backend.core.error import NotFoundError, ValidationError
from database.model.treasury.fund_reservation import FundReservation
from uuid import uuid4



class CashPositionProvider:
    """
    Data provider responsible for CashPosition persistence.

    Responsibilities:

    - Fetch provider balance snapshot
    - Retrieve normalized cash positions
    - List positions by currency
    - Update balances after external sync or treasury operations

    Does NOT handle:

    - Reservations
    - Funding transfers
    - Liquidity aggregation
    """

    def __init__(self, session: Session):
        """
        Initialize provider with database session.

        Args:
            session (Session): Active SQLModel session.
        """
        self.session = session

    # ------------------------------------------------------------
    # External provider sync
    # ------------------------------------------------------------

    def fetch_balance(self, provider: str, account_id: str) -> CashPosition:
        """
        Fetch stored balance snapshot for provider account.

        NOTE:
        This returns stored balance.
        External provider API sync should be handled elsewhere.

        Args:
            provider (str): Provider identifier.
            account_id (str): Provider account ID.

        Returns:
            CashPosition

        Raises:
            NotFoundError: If position does not exist.
        """

        statement = select(CashPosition).where(
            CashPosition.provider == provider,
            CashPosition.account_id == account_id
        )

        position = self.session.exec(statement).first()

        if not position:
            raise NotFoundError("Cash Position", f"{provider}:{account_id}")

        return position

    # ------------------------------------------------------------
    # Single position
    # ------------------------------------------------------------

    def get_cash_position(
        self,
        provider: str,
        account_id: str
    ) -> CashPosition:
        """
        Retrieve cash position.

        Args:
            provider (str)
            account_id (str)

        Returns:
            CashPosition

        Raises:
            NotFoundError
        """

        return self.fetch_balance(provider, account_id)

    # ------------------------------------------------------------
    # List positions
    # ------------------------------------------------------------

    def list_cash_positions(
        self,
        currency_code: Optional[str] = None
    ) -> List[CashPosition]:
        """
        List all cash positions.

        Args:
            currency_code (optional)

        Returns:
            List[CashPosition]
        """

        statement = select(CashPosition)

        if currency_code:
            statement = statement.where(
                CashPosition.currency_code == currency_code
            )

        return list(self.session.exec(statement).all())

    # ------------------------------------------------------------
    # Balance update (internal use only)
    # ------------------------------------------------------------

    def update_balance(
        self,
        provider: str,
        account_id: str,
        total_balance: float,
        available_balance: float,
        reserved_balance: float
    ) -> CashPosition:
        """
        Update stored balance snapshot.

        Used by:

        - FundingProvider
        - ReservationProvider
        - External sync service

        Args:
            provider (str)
            account_id (str)
            total_balance (float)
            available_balance (float)
            reserved_balance (float)

        Returns:
            Updated CashPosition
        """

        position = self.fetch_balance(provider, account_id)

        position.total_balance = total_balance
        position.available_balance = available_balance
        position.reserved_balance = reserved_balance
        position.last_synced_at = datetime.utcnow()

        self.session.add(position)
        self.session.commit()
        self.session.refresh(position)

        return position

    # ------------------------------------------------------------
    # Create position
    # ------------------------------------------------------------

    def create_cash_position(
        self,
        provider: str,
        account_id: str,
        currency_code: str,
        total_balance: float = 0.0,
        available_balance: float = 0.0,
        reserved_balance: float = 0.0,
        note: Optional[str] = None
    ) -> CashPosition:
        """
        Create new provider cash position.

        Used during provider onboarding.

        Returns:
            CashPosition
        """

        existing = self.session.exec(
            select(CashPosition).where(
                CashPosition.provider == provider,
                CashPosition.account_id == account_id
            )
        ).first()

        if existing:
            raise ValidationError(
                "Cash position already exists"
            )

        position = CashPosition(
            provider=provider,
            account_id=account_id,
            currency_code=currency_code,
            total_balance=total_balance,
            available_balance=available_balance,
            reserved_balance=reserved_balance,
            last_synced_at=datetime.utcnow(),
            note=note
        )

        self.session.add(position)
        self.session.commit()
        self.session.refresh(position)

        return position
    
    # ------------------------------------------------------------
    # Fund reservation operations
    # ------------------------------------------------------------
    def reserve_funds(self, reserve_in: ReserveFundsCreate) -> FundReservation:
        """
        Reserve funds for a pending transaction.
        Deducts available_balance without moving actual money.

        Raises ValidationError if insufficient funds.
        """
        position = self.fetch_balance(reserve_in.provider, reserve_in.account_id)

        if position.available_balance < reserve_in.amount:
            raise ValidationError(
                f"Insufficient funds: available {position.available_balance}, requested {reserve_in.amount}"
            )

        # Update balances
        position.reserved_balance += float(reserve_in.amount)
        position.available_balance -= float(reserve_in.amount)

        # Create reservation record
        reservation = FundReservation(
            reservation_id=str(uuid4()),
            cash_position_id=position.id,
            provider=reserve_in.provider,
            account_id=reserve_in.account_id,
            amount=float(reserve_in.amount),
            currency_code=position.currency_code,
            transaction_ref=reserve_in.transaction_ref,
            status="ACTIVE"
        )

        self.session.add(position)
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)

        return reservation

    def release_reservation(self, reservation_id: str) -> FundReservation:
        """
        Release a previously reserved fund.
        Adds amount back to available_balance.
        """
        reservation = self.session.get(FundReservation, reservation_id)
        if not reservation:
            raise NotFoundError("FundReservation", reservation_id)

        if reservation.status != "ACTIVE":
            raise ValidationError(f"Reservation {reservation_id} is not active and cannot be released")

        # Update cash position
        position = self.fetch_balance(reservation.provider, reservation.account_id)
        position.reserved_balance -= reservation.amount
        position.available_balance += reservation.amount

        # Update reservation
        reservation.status = "RELEASED"
        reservation.released_at = datetime.utcnow()

        self.session.add(position)
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)

        return reservation

    def confirm_reservation(self, reservation_id: str) -> FundReservation:
        """
        Confirm a reservation after transaction execution.
        Deducts reserved balance permanently.
        """
        reservation = self.session.get(FundReservation, reservation_id)
        if not reservation:
            raise NotFoundError("FundReservation", reservation_id)

        if reservation.status != "ACTIVE":
            raise ValidationError(f"Reservation {reservation_id} is not active and cannot be confirmed")

        # Update cash position
        position = self.fetch_balance(reservation.provider, reservation.account_id)
        position.reserved_balance -= reservation.amount
        position.total_balance -= reservation.amount

        # Update reservation
        reservation.status = "CONFIRMED"
        reservation.released_at = datetime.utcnow()

        self.session.add(position)
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)

        return reservation

