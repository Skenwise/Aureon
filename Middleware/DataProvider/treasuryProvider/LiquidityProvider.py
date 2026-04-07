"""
Liquidity Data Provider.

Aggregates liquidity across all provider accounts using CashPosition records.

This provider is strictly READ-ONLY.
It never mutates balances.
It acts as the real-time treasury liquidity oracle.
"""

from typing import List, Dict
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from database.model.treasury.cash_position import CashPosition

from backend.core.error import NotFoundError, ValidationError


class LiquidityProvider:
    """
    Data provider responsible for liquidity aggregation.

    Provides:

    - Currency liquidity snapshot
    - Total liquidity across currencies
    - Sufficiency checks

    Uses CashPosition as single source of truth.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize provider with database session.

        Args:
            session (AsyncSession): Active SQLAlchemy async session.
        """
        self.session = session

    # ------------------------------------------------------------
    # Liquidity snapshot
    # ------------------------------------------------------------

    async def get_liquidity(self, currency_code: str) -> Dict:
        """
        Get aggregated liquidity for a single currency.

        Args:
            currency_code (str): ISO currency code.

        Returns:
            Dict: Liquidity snapshot.

        Raises:
            NotFoundError: If no positions exist.
            ValidationError: If invalid currency.
        """

        if not currency_code or len(currency_code) != 3:
            raise ValidationError("Invalid currency code")

        statement = (
            select(
                CashPosition.currency_code,
                func.sum(CashPosition.total_balance),
                func.sum(CashPosition.available_balance),
                func.sum(CashPosition.reserved_balance)
            )
            .where(CashPosition.currency_code == currency_code)
            .group_by(CashPosition.currency_code)
        )

        result = await self.session.execute(statement)
        row = result.first()

        if not row:
            raise NotFoundError("Liquidity", f"Currency: {currency_code}")

        currency, total, available, reserved = row

        return {
            "currency_code": currency,
            "total_balance": total or 0,
            "available_balance": available or 0,
            "reserved_balance": reserved or 0,
        }

    # ------------------------------------------------------------
    # All liquidity
    # ------------------------------------------------------------

    async def get_total_liquidity(self) -> List[Dict]:
        """
        Get liquidity across all currencies.

        Returns:
            List[Dict]: Liquidity per currency.
        """

        statement = (
            select(
                CashPosition.currency_code,
                func.sum(CashPosition.total_balance),
                func.sum(CashPosition.available_balance),
                func.sum(CashPosition.reserved_balance)
            )
            .group_by(CashPosition.currency_code)
        )

        result = await self.session.execute(statement)
        rows = result.all()

        liquidity = []

        for currency, total, available, reserved in rows:
            liquidity.append({
                "currency_code": currency,
                "total_balance": total or 0,
                "available_balance": available or 0,
                "reserved_balance": reserved or 0,
            })

        return liquidity

    # ------------------------------------------------------------
    # Sufficiency check
    # ------------------------------------------------------------

    async def check_sufficient_funds(
        self,
        currency_code: str,
        required_amount: Decimal
    ) -> bool:
        """
        Check if sufficient available liquidity exists.

        Args:
            currency_code (str): Currency code.
            required_amount (Decimal): Required amount.

        Returns:
            bool: True if sufficient funds exist.

        Raises:
            ValidationError: If invalid input.
        """

        if required_amount <= 0:
            raise ValidationError("Required amount must be positive")

        liquidity = await self.get_liquidity(currency_code)

        available = Decimal(str(liquidity["available_balance"]))

        return available >= required_amount
