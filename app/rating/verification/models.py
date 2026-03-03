import datetime
from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


class Result(float, Enum):
    WIN = 1.0
    DRAW = 0.5
    LOSS = 0.0


class GameType(str, Enum):
    STANDARD = "STANDARD"
    RAPID = "RAPID"
    BLITZ = "BLITZ"


class RatingSource(str, Enum):
    KS = "knsb-standard"     # knsb klassieke rating
    KR = "knsb-rapid"     # knsb rapid rating
    KB = "knsb-blitz"     # knsb blitz rating
    FS = "fide-standard"     # fide klassieke rating
    FR = "fide-rapid"     # fide rapid rating
    FB = "fide-blitz"     # fide blitz rating
    LPR = "lpr"    # de lijstprestatierating
    TLPR = "tlpr"  # de tegenstander-lijstprestatierating
    CALC = "calculated"  # de voorspelde of berekende rating


class Player(BaseModel):
    knsb_id: Annotated[int | None, Field(gt=0)] = None
    fide_id: Annotated[int | None, Field(gt=0)] = None

    @model_validator(mode='after')
    def check_knsb_or_fide(self) -> Self:
        if not (self.knsb_id or self.fide_id):
            raise ValueError("Of de KNSB ID of de FIDE ID van de speler moet gegeven zijn!")
        return self


class RatingPeriod(BaseModel):
    month: Annotated[int, Field(gt=0, le=12)]
    year: Annotated[int, Field(gt=0)]

    @model_validator(mode='after')
    def check_game_future(self) -> Self:
        if self.as_date() > datetime.date.today():
            raise ValueError("Partijen in toekomstige ratingperioden kunnen niet berekend worden.")
        
        return self

    def as_date(self) -> datetime.date:
        return datetime.date(self.year, self.month, 1)


class Game(BaseModel):
    opponent: Player
    result: Result
    period: RatingPeriod


class GameList(BaseModel):
    player: Player
    game_type: GameType
    period: RatingPeriod
    games: list[Game]

    @model_validator(mode='after')
    def check_game_data(self) -> Self:
        # check of alle data van de partijen een beetje normaal zijn
        # in de detail kan deze wellicht wat specifieker?
        if any(self.period.as_date() < p.period.as_date()
               for p in self.games):
            raise ValueError("Datum van partij is na berekendatum.")
        
        # TODO wat doen we met data heel ver in het verleden?
        # waarschijnlijk tot 2 jaar geleden...

        return self


class RatingResult(BaseModel):
    rating: int
    nv_value: float
    source: RatingSource
    period: RatingPeriod


class GameCalculation(BaseModel):
    game: Game
    player_rating: RatingResult
    opponent_rating: RatingResult
    wwe: float
    k_factor: float
    delta: float
    counts: Literal[True] = True


class GameDoesNotCount(BaseModel):
    game: Game
    reason: str
    counts: Literal[False] = False


GameResult = GameCalculation | GameDoesNotCount


class LprLimitation(BaseModel):
    lpr: int | None
    lower_limit: int | None
    upper_limit: int | None


class ListCalculation(BaseModel):
    old_rating: RatingResult
    new_rating: RatingResult
    played: int
    delta: int
    bonus: int
    lpr_limitation: LprLimitation
    games: list[GameResult]
