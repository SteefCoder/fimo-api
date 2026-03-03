from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class RatingPeriod:
    month: int
    year: int

    def __str__(self) -> str:
        return self.as_date().isoformat()
    
    def __hash__(self) -> int:
        return self.as_date().__hash__()

    @classmethod
    def current(cls) -> RatingPeriod:
        today = datetime.date.today()
        return cls(today.month, today.year)

    @classmethod
    def from_date(cls, date: datetime.date) -> RatingPeriod:
        return cls(date.month, date.year)
    
    @classmethod
    def from_iso(cls, date: str) -> RatingPeriod:
        return cls.from_date(datetime.date.fromisoformat(date))

    def as_date(self) -> datetime.date:
        return datetime.date(self.year, self.month, 1)
