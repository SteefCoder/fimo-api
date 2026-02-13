from dataclasses import dataclass
from enum import Enum
from typing import Literal

from ..periode import RatingPeriode


class Resultaat(float, Enum):
    WINST = 1.0
    REMISE = 0.5
    VERLIES = 0.0


class PartijType(str, Enum):
    KLASSIEK = "KLASSIEK"
    RAPID = "RAPID"
    BLITZ = "BLITZ"


class RatingBron(str, Enum):
    KS = "knsb-klassiek"     # knsb klassieke rating
    KR = "knsb-rapid"     # knsb rapid rating
    KB = "knsb-snel"     # knsb blitz rating
    FS = "fide-klassiek"     # fide klassieke rating
    FR = "fide-rapid"     # fide rapid rating
    FB = "fide-snel"     # fide blitz rating
    LPR = "lpr"    # de lijstprestatierating
    TLPR = "tlpr"  # de tegenstander-lijstprestatierating
    CALC = "berekening"  # de voorspelde of berekende rating


@dataclass(frozen=True)
class Speler:
    knsb_id: int | None
    fide_id: int | None


@dataclass
class Partij:
    tegenstander: Speler
    resultaat: Resultaat
    periode: RatingPeriode


@dataclass
class PartijLijst:
    speler: Speler
    partijtype: PartijType
    periode: RatingPeriode
    partijen: list[Partij]


@dataclass
class RatingContext:
    partijtype: PartijType
    periode: RatingPeriode
    lpr: int | None = None


@dataclass
class RatingResultaat:
    rating: int
    nv_waarde: float
    bron: RatingBron
    periode: RatingPeriode


@dataclass
class PartijBerekening:
    partij: Partij
    speler_rating: RatingResultaat
    tegenstander_rating: RatingResultaat
    wwe: float
    k_waarde: float
    delta: float
    telt_mee: Literal[True] = True


@dataclass
class PartijTeltNietMee:
    partij: Partij
    reden: str
    telt_mee: Literal[False] = False


PartijResultaat = PartijBerekening | PartijTeltNietMee


@dataclass
class LprLimitering:
    lpr: int | None
    ondergrens: int | None
    bovengrens: int | None


@dataclass
class LijstBerekening:
    oude_rating: RatingResultaat
    nieuwe_rating: RatingResultaat
    gespeeld: int
    delta: int
    bonus: int
    lpr: LprLimitering
    partijen: list[PartijResultaat]
