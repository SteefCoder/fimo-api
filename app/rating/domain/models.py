from dataclasses import dataclass
from enum import Enum
from typing import Literal

from ..period import RatingPeriod


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


@dataclass(frozen=True)
class Player:
    knsb_id: int | None
    fide_id: int | None


@dataclass
class RatingContext:
    game_type: GameType
    period: RatingPeriod
    lpr: int | None = None


@dataclass
class Game:
    opponent: Player
    result: Result
    period: RatingPeriod


@dataclass
class GameList:
    player: Player
    game_type: GameType
    period: RatingPeriod
    games: list[Game]


@dataclass
class RatingResult:
    rating: int
    nv_value: float
    source: RatingSource
    period: RatingPeriod


@dataclass
class GameCalculation:
    game: Game
    player_rating: RatingResult
    opponent_rating: RatingResult
    wwe: float
    k_factor: float
    delta: float
    counts: Literal[True] = True


@dataclass
class GameDoesNotCount:
    game: Game
    reason: str
    counts: Literal[False] = False


GameResult = GameCalculation | GameDoesNotCount


@dataclass
class LprLimitation:
    lpr: int | None
    lower_limit: int | None
    upper_limit: int | None


@dataclass
class ListCalculation:
    old_rating: RatingResult
    new_rating: RatingResult
    played: int
    delta: int
    bonus: int
    lpr_limitation: LprLimitation
    games: list[GameResult]
