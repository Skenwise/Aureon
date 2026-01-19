from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Union, Any

@dataclass(frozen=True)
class DateHandler:
    value_date: date
    posting_datetime: datetime

    def __init__(self, data: Union[date, datetime]):
        if isinstance(data, datetime):
            value_date = data.date()
            posting_datetime = data
        elif isinstance(data, date):
            value_date = data
            posting_datetime = datetime.combine(data, time.min, tzinfo=timezone.utc)
        else:
            raise TypeError("Input must be a date or datetime instance")
        
        object.__setattr__(self, 'value_date', value_date)
        object.__setattr__(self, 'posting_datetime', posting_datetime)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, DateHandler) and self.value_date == other.value_date and self.posting_datetime == other.posting_datetime

    def __lt__(self, other: 'DateHandler') -> bool:
        if not isinstance(other, DateHandler):
            return NotImplemented
        return self.posting_datetime < other.posting_datetime

    def __le__(self, other: 'DateHandler') -> bool:
        if not isinstance(other, DateHandler):
            return NotImplemented
        return self.posting_datetime <= other.posting_datetime

    def __gt__(self, other: 'DateHandler') -> bool:
        if not isinstance(other, DateHandler):
            return NotImplemented
        return self.posting_datetime > other.posting_datetime

    def __ge__(self, other: 'DateHandler') -> bool:
        if not isinstance(other, DateHandler):
            return NotImplemented
        return self.posting_datetime >= other.posting_datetime

    def __repr__(self) -> str:
        return f"DateHandler(value_date={self.value_date.isoformat()}, posting_datetime={self.posting_datetime.isoformat()})"
