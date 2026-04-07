# Middleware/DataProvider/currencyProvider.py
"""
Currency data provider.

Provides database access for Currency and ExchangeRate models.
Returns ProviderOutput schemas, NOT SQLModel objects.

All errors are translated to Aureon domain errors.
All operations are logged with structured context.
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError

from database.model.misc.currency import Currency
from database.model.misc.exchange_rate import ExchangeRate
from backend.core.error import (
    NotFoundError,
    CalculationError,
    ValidationError,
    AureonError,
)
from schemas.provider.currency import CurrencyProviderOutput, CurrencyProviderFilter

logger = logging.getLogger(__name__)


class CurrencyProvider:
    """
    Provider for currency and exchange rate queries.
    Encapsulates all database logic for currency operations and FX lookups.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for DB operations.
        """
        self.session = session

    # ----------------- Currency Operations ----------------- #

    async def get_currency_by_code(self, code: str) -> CurrencyProviderOutput:
        """
        Retrieve a currency by its ISO code.

        Args:
            code (str): Currency ISO code.

        Returns:
            CurrencyProviderOutput: Currency data.

        Raises:
            NotFoundError: If no currency with the given code exists.
            ValidationError: If code is invalid.
            AureonError: For unexpected database errors.
        """
        # Input validation
        if not code or len(code.strip()) == 0:
            logger.warning(f"Invalid currency code provided: '{code}'")
            raise ValidationError("Currency code cannot be empty")

        code = code.upper().strip()
        if len(code) != 3:
            logger.warning(f"Invalid currency code length: '{code}'")
            raise ValidationError(f"Currency code must be 3 characters: '{code}'")

        try:
            logger.debug(f"Fetching currency by code: {code}")
            stmt = select(Currency).where(Currency.code == code)  # type: ignore
            result = await self.session.execute(stmt)
            currency = result.scalar_one_or_none()

            if not currency:
                logger.warning(f"Currency not found: {code}")
                raise NotFoundError("Currency", code)

            logger.info(f"Currency retrieved successfully: {code}")
            return CurrencyProviderOutput.model_validate(currency)

        except NotFoundError:
            # Re-raise domain errors
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching currency {code}: {str(e)}",
                exc_info=True,
            )
            raise AureonError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching currency {code}: {str(e)}",
                exc_info=True,
            )
            raise AureonError(f"Unexpected error: {str(e)}")

    async def list_currencies(
        self, filter_params: Optional[CurrencyProviderFilter] = None
    ) -> List[CurrencyProviderOutput]:
        """
        List all available currencies with optional filtering.

        Args:
            filter_params (CurrencyProviderFilter, optional): Filters for listing.

        Returns:
            List[CurrencyProviderOutput]: All currencies in the system.

        Raises:
            AureonError: For database errors.
        """
        try:
            logger.debug("Listing currencies")
            stmt = select(Currency)

            # Apply filters if provided
            if filter_params:
                if filter_params.code:
                    stmt = stmt.where(Currency.code == filter_params.code)  # type: ignore
                    logger.debug(f"Filtering by code: {filter_params.code}")

                if filter_params.name_contains:
                    stmt = stmt.where(Currency.name.contains(filter_params.name_contains))  # type: ignore
                    logger.debug(
                        f"Filtering by name contains: {filter_params.name_contains}"
                    )

                stmt = stmt.offset(filter_params.offset).limit(filter_params.limit)
                logger.debug(
                    f"Pagination: offset={filter_params.offset}, limit={filter_params.limit}"
                )

            result = await self.session.execute(stmt)
            currencies = list(result.scalars().all())

            logger.info(f"Retrieved {len(currencies)} currencies")
            return [CurrencyProviderOutput.model_validate(c) for c in currencies]

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while listing currencies: {str(e)}", exc_info=True
            )
            raise AureonError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error while listing currencies: {str(e)}", exc_info=True
            )
            raise AureonError(f"Unexpected error: {str(e)}")

    # ----------------- Exchange Rates ----------------- #

    async def get_rate(self, base_currency: str, quote_currency: str) -> float:
        """
        Retrieve the latest exchange rate from base to quote currency.

        Args:
            base_currency (str): ISO code of base currency.
            quote_currency (str): ISO code of quote currency.

        Returns:
            float: Conversion rate.

        Raises:
            ValidationError: If currency codes are invalid.
            NotFoundError: If rate not found.
            AureonError: For database errors.
        """
        # Input validation
        if not base_currency or len(base_currency.strip()) != 3:
            raise ValidationError(f"Invalid base currency code: '{base_currency}'")
        if not quote_currency or len(quote_currency.strip()) != 3:
            raise ValidationError(f"Invalid quote currency code: '{quote_currency}'")

        base = base_currency.upper().strip()
        quote = quote_currency.upper().strip()

        try:
            logger.debug(f"Fetching exchange rate: {base} -> {quote}")
            stmt = (
                select(ExchangeRate)
                .where(ExchangeRate.base_currency == base)  # type: ignore
                .where(ExchangeRate.quote_currency == quote)  # type: ignore
                .order_by(desc(ExchangeRate.valid_from))  # type: ignore
            )
            result = await self.session.execute(stmt)
            rate_obj = result.scalar_one_or_none()

            if not rate_obj:
                logger.warning(f"Exchange rate not found: {base} -> {quote}")
                raise NotFoundError("ExchangeRate", f"{base}->{quote}")

            logger.info(f"Exchange rate retrieved: {base} -> {quote} = {rate_obj.rate}")
            return rate_obj.rate

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching rate {base}->{quote}: {str(e)}",
                exc_info=True,
            )
            raise AureonError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching rate {base}->{quote}: {str(e)}",
                exc_info=True,
            )
            raise AureonError(f"Unexpected error: {str(e)}")

    async def list_exchange_rates(self) -> List[ExchangeRate]:
        """
        List all exchange rates.

        Returns:
            List[ExchangeRate]: All exchange rates in the system.

        Raises:
            AureonError: For database errors.
        """
        try:
            logger.debug("Listing exchange rates")
            stmt = select(ExchangeRate)
            result = await self.session.execute(stmt)
            rates = list(result.scalars().all())
            logger.info(f"Retrieved {len(rates)} exchange rates")
            return rates

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while listing exchange rates: {str(e)}", exc_info=True
            )
            raise AureonError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error while listing exchange rates: {str(e)}",
                exc_info=True,
            )
            raise AureonError(f"Unexpected error: {str(e)}")

    # ----------------- FX Revaluation ----------------- #

    def revalue_balance(
        self, balance: float, old_rate: float, new_rate: float
    ) -> float:
        """
        Calculate unrealized gain/loss for a balance given old and new FX rates.

        Args:
            balance (float): Balance amount in foreign currency.
            old_rate (float): Previous FX rate to base currency.
            new_rate (float): Current FX rate to base currency.

        Returns:
            float: Gain (positive) or loss (negative).

        Raises:
            CalculationError: If input values are invalid.
        """
        logger.debug(
            f"Revaluing balance: balance={balance}, old_rate={old_rate}, new_rate={new_rate}"
        )

        if balance < 0:
            logger.warning(f"Negative balance provided: {balance}")
            raise CalculationError("Balance cannot be negative for revaluation")

        if old_rate <= 0:
            logger.warning(f"Invalid old_rate: {old_rate}")
            raise CalculationError(f"Old FX rate must be greater than zero: {old_rate}")

        if new_rate <= 0:
            logger.warning(f"Invalid new_rate: {new_rate}")
            raise CalculationError(f"New FX rate must be greater than zero: {new_rate}")

        result = round(balance * (new_rate - old_rate), 2)
        logger.info(f"Revaluation result: {result} (gain/loss)")
        return result
