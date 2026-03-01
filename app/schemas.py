import datetime

from pydantic import BaseModel


class KnsbPlayerResponse(BaseModel):
    knsb_id: int
    fide_id: int | None
    name: str
    title: str | None
    fed: str
    birthyear: int
    sex: str


class FidePlayerResponse(BaseModel):
    fide_id: int
    name: str
    title: str | None
    woman_title: str | None
    other_titles: str | None
    fed: str
    birthyear: int
    sex: str
    active: bool


class KnsbRatingResponse(BaseModel):
    knsb_id: int
    date: datetime.date
    title: str | None
    standard_rating: int | None
    standard_games: int | None
    rapid_rating: int | None
    rapid_games: int | None
    blitz_rating: int | None
    blitz_games: int | None
    junior_rating: int | None
    junior_games: int | None


class FideRatingResponse(BaseModel):
    fide_id: int
    date: datetime.date
    title: str | None
    woman_title: str | None
    other_titles: str | None
    active: bool

    standard_rating: int | None
    standard_games: int | None
    standard_k: int | None
    rapid_rating: int | None
    rapid_games: int | None
    rapid_k: int | None
    blitz_rating: int | None
    blitz_games: int | None
    blitz_k: int | None


class SuggestPlayerResponse(BaseModel):
    id: int
    knsb_id: int
    fide_id: int
    name: int
