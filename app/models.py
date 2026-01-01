import datetime
from dataclasses import asdict, dataclass

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


@dataclass(init=False)
class KnsbPlayer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fide: Mapped[int] = mapped_column(Integer, ForeignKey("fide.ID"))
    full_name: Mapped[str]
    title: Mapped[str]
    federation: Mapped[str]
    birthyear: Mapped[int]
    sex: Mapped[str]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(init=False)
class KnsbRating(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    standard_rating: Mapped[int]
    standard_games: Mapped[int]
    rapid_rating: Mapped[int]
    rapid_games: Mapped[int]
    blitz_rating: Mapped[int]
    blitz_games: Mapped[int]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self) | {"Date": self.date.isoformat()}


@dataclass(init=False)
class FidePlayer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    title: Mapped[str]
    federation: Mapped[str]
    birthyear: Mapped[int]
    sex: Mapped[str]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(init=False)
class FideRating(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    standard_rating: Mapped[int]
    standard_k: Mapped[int]
    rapid_rating: Mapped[int]
    rapid_k: Mapped[int]
    blitz_rating: Mapped[int]
    blitz_k: Mapped[int]

    def asdict(self) -> dict[str, str | int]:
        return asdict(self) | {"Date": self.date.isoformat()}
