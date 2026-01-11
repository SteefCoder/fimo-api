import datetime
from dataclasses import dataclass
from enum import Enum, auto

from periode import RatingPeriode
from speler import Speler


class Resultaat(Enum):
    WINST = 1.0
    REMISE = 0.5
    VERLIES = 0.0


class PartijType(Enum):
    KLASSIEK = auto()
    RAPID = auto()
    BLITZ = auto()


class Flag(Enum):
    KS = auto()     # knsb klassieke rating
    KR = auto()     # knsb rapid rating
    KB = auto()     # knsb blitz rating
    FS = auto()     # fide klassieke rating
    FR = auto()     # fide rapid rating
    FB = auto()     # fide blitz rating
    LPR = auto()    # de lijstprestatierating
    TLPR = auto()   # de tegenstander-lijstprestatierating


@dataclass(frozen=True)
class RatingBron:
    bron: Flag
    periode: RatingPeriode


@dataclass(frozen=True)
class RatingResultaat:
    rating: int
    nv_waarde: float
    bron: RatingBron


@dataclass
class RatingContext:
    partijtype: PartijType
    periode: RatingPeriode
    lpr: int | None = None


@dataclass(frozen=True)
class Partij:
    speler: Speler
    tegenstander: Speler
    resultaat: Resultaat
    ctx: RatingContext


@dataclass(frozen=True)
class PartijResultaat:
    speler_bron: RatingBron
    tegenstander_bron: RatingBron
    wwe: float
    k: float
    delta: float
