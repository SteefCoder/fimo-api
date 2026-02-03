import datetime
from dataclasses import dataclass
from enum import Enum, auto

from .periode import RatingPeriode
from .speler import Speler


class Resultaat(Enum):
    WINST = 1.0
    REMISE = 0.5
    VERLIES = 0.0


class PartijType(Enum):
    KLASSIEK = "KLASSIEK"
    RAPID = "RAPID"
    BLITZ = "BLITZ"


class Flag(str, Enum):
    KS = "knsb-standard"     # knsb klassieke rating
    KR = "knsb-rapid"     # knsb rapid rating
    KB = "knsb-blitz"     # knsb blitz rating
    FS = "fide-standard"     # fide klassieke rating
    FR = "fide-rapid"     # fide rapid rating
    FB = "fide-blitz"     # fide blitz rating
    LPR = "lpr"    # de lijstprestatierating
    TLPR = "tlpr"  # de tegenstander-lijstprestatierating


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
    speler_rating: RatingResultaat
    tegenstander_rating: RatingResultaat
    wwe: float
    k: float
    delta: float


@dataclass(frozen=True)
class BerekeningsResultaat:
    nieuwe_rating: int
    oude_rating: RatingResultaat
    partijen: list[PartijResultaat | None]
    delta: int
    bonus: int
    lpr: int
