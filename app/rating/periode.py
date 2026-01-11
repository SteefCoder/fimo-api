from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class RatingPeriode:
    maand: int
    jaar: int

    def __str__(self) -> str:
        return self.als_datum().isoformat()
    
    def __hash__(self) -> int:
        return self.als_datum().__hash__()

    @classmethod
    def huidige_periode(cls) -> RatingPeriode:
        vandaag = datetime.date.today()
        return cls(vandaag.month, vandaag.year)

    @classmethod
    def uit_datum(cls, datum: datetime.date) -> RatingPeriode:
        return cls(datum.month, datum.year)
    
    def als_datum(self) -> datetime.date:
        return datetime.date(self.jaar, self.maand, 1)
