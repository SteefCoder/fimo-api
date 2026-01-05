import datetime
from dataclasses import asdict, dataclass

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


@dataclass(init=False)
class KnsbPlayer(db.Model):
    knsb_id: Mapped[int] = mapped_column(primary_key=True)
    fide_id: Mapped[int] = mapped_column(Integer, ForeignKey("fide.id"))
    name: Mapped[str]
    title: Mapped[str]
    fed: Mapped[str]
    birthyear: Mapped[int]
    sex: Mapped[str]
    start_date: Mapped[datetime.date]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self) | {"start_date": self.start_date.isoformat()}


@dataclass(init=False)
class KnsbRating(db.Model):
    knsb_id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    standard_rating: Mapped[int]
    standard_games: Mapped[int]
    rapid_rating: Mapped[int]
    rapid_games: Mapped[int]
    blitz_rating: Mapped[int]
    blitz_games: Mapped[int]
    junior_rating: Mapped[int]
    junior_games: Mapped[int]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self) | {"date": self.date.isoformat()}


@dataclass(init=False)
class FidePlayer(db.Model):
    fide_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    title: Mapped[str]
    woman_title: Mapped[str]
    other_titles: Mapped[str]
    fed: Mapped[str]
    birthyear: Mapped[int]
    sex: Mapped[str]
    active: bool

    def asdict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(init=False)
class FideRating(db.Model):
    fide_id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    standard_rating: Mapped[int]
    standard_k: Mapped[int]
    rapid_rating: Mapped[int]
    rapid_k: Mapped[int]
    blitz_rating: Mapped[int]
    blitz_k: Mapped[int]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self) | {"date": self.date.isoformat()}
