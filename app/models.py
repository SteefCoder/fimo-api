from typing import Annotated

from fastapi import Depends
from sqlmodel import Date, Field, Session, SQLModel, create_engine


class KnsbPlayer(SQLModel, table=True):
    knsb_id: int = Field(primary_key=True)
    fide_id: int = Field(foreign_key='fide_player.fide_id')
    name: str
    title: str | None = None
    fed: str
    birthyear: int
    sex: str


class KnsbRating(SQLModel, table=True):
    knsb_id: int = Field(primary_key=True)
    date: Date = Field(primary_key=True)
    title: str | None = None
    standard_rating: int | None = None
    standard_games: int | None = None
    rapid_rating: int | None = None
    rapid_games: int | None = None
    blitz_rating: int | None = None
    blitz_games: int | None = None
    junior_rating: int | None = None
    junior_games: int | None = None


class FidePlayer(SQLModel, table=True):
    fide_id: int = Field(primary_key=True)
    name: str
    title: str | None = None
    woman_title: str | None = None
    other_titles: str | None = None
    fed: str
    birthyear: int
    sex: str
    active: bool


class FideRating(SQLModel, table=True):
    fide_id: int = Field(primary_key=True)
    date: Date = Field(primary_key=True)

    active: bool

    title: str | None = None
    woman_title: str | None = None
    other_titles: str | None = None

    standard_rating: int | None = None
    standard_games: int | None = None
    standard_k: int | None = None

    rapid_rating: int | None = None
    rapid_games: int | None = None
    rapid_k: int | None = None

    blitz_rating: int | None = None
    blitz_games: int | None = None
    blitz_k: int | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
