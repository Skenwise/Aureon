# money.py defines an immutable, currency-aware value object for all monetary amounts, handling precise arithmetic, rounding, and preventing cross-currency errors.
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Any
from dataclasses import dataclass
getcontext().prec = 28  # Set a high precision for Decimal operations
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(self.amount))
        if not isinstance(self.currency, str):
            raise TypeError("Currency must be a string")

    def _check_currency(self, other: 'Money'):
        if self.currency != other.currency:
            raise ValueError(f"Cannot operate on different currencies: {self.currency} and {other.currency}")

    def __add__(self, other: 'Money') -> 'Money':
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Any) -> 'Money':
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError("Factor must be a number")
        return Money((self.amount * Decimal(factor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), self.currency)

    def __truediv__(self, divisor: Any) -> 'Money':
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Divisor must be a number")
        return Money((self.amount / Decimal(divisor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), self.currency)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: 'Money') -> bool:
        self._check_currency(other)
        return self.amount < other.amount

    def __le__(self, other: 'Money') -> bool:
        self._check_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: 'Money') -> bool:
        self._check_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: 'Money') -> bool:
        self._check_currency(other)
        return self.amount >= other.amount

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"