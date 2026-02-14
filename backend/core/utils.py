from typing import Any, TypeVar, Callable
from backend.core.error import ValidationError

T = TypeVar("T")


def require(data: dict, key: str, cast: Callable[[Any], T]) -> T:
    """
    Extract and cast required field from dict safely.

    Raises ValidationError if missing or invalid.
    """
    value = data.get(key)

    if value is None:
        raise ValidationError(f"{key} is required")

    try:
        return cast(value)
    except Exception:
        raise ValidationError(f"{key} is invalid")
    
from datetime import date, datetime
from typing import Any
from backend.core.error import ValidationError


def cast_date(value: Any) -> date:
    """
    Safely cast value to date.

    Accepts:
    - date
    - datetime
    - ISO string (YYYY-MM-DD)
    """
    if isinstance(value, date):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValidationError("Invalid date format, expected YYYY-MM-DD")

    raise ValidationError("Invalid date value")

