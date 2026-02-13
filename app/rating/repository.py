import datetime
from typing import Protocol

from .periode import RatingPeriode


class KnsbPlayer(Protocol):
    knsb_id: int
    fide_id: int
    fed: str
    birthyear: int


class FidePlayer(Protocol):
    fide_id: int
    birthyear: int


class KnsbRating(Protocol):
    knsb_id: int
    date: datetime.date

    standard_rating: int | None
    standard_games: int | None
    rapid_rating: int | None
    rapid_games: int | None
    blitz_rating: int | None
    blitz_games: int | None


class FideRating(Protocol):
    fide_id: int
    date: datetime.date

    standard_rating: int | None
    standard_k: int | None
    rapid_rating: int | None
    rapid_k: int | None
    blitz_rating: int | None
    blitz_k: int | None


class RatingRepository(Protocol):
    def get_knsb(self, knsb_id: int) -> KnsbPlayer: ...

    def get_fide(self, fide_id: int) -> FidePlayer: ...

    def get_knsb_from_fide(self, fide_id: int) -> KnsbPlayer | None: ...

    def get_knsb_rating(self, knsb_id: int, periode: RatingPeriode) -> KnsbRating | None: ...

    def get_fide_rating(self, fide_id: int, periode: RatingPeriode) -> FideRating | None: ...

    def heeft_partij_gespeeld(self, knsb_id: int) -> bool: ...
