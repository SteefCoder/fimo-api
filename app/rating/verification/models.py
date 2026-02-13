import datetime
from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


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


class Speler(BaseModel):
    knsb_id: Annotated[int | None, Field(gt=0)] = None
    fide_id: Annotated[int | None, Field(gt=0)] = None

    @model_validator(mode='after')
    def check_knsb_of_fide(self) -> Self:
        if not (self.knsb_id or self.fide_id):
            raise ValueError("Of de KNSB ID of de FIDE ID van de speler moet gegeven zijn!")
        return self


class RatingPeriode(BaseModel):
    maand: Annotated[int, Field(gt=0, le=12)]
    jaar: Annotated[int, Field(gt=0)]

    @model_validator(mode='after')
    def check_partij_toekomst(self) -> Self:
        if self.als_datum() > datetime.date.today():
            raise ValueError("Partijen in toekomstige ratingperioden kunnen niet berekend worden.")
        
        return self

    def als_datum(self) -> datetime.date:
        return datetime.date(self.jaar, self.maand, 1)


class Partij(BaseModel):
    tegenstander: Speler
    resultaat: Resultaat
    periode: RatingPeriode


class PartijLijst(BaseModel):
    speler: Speler
    partijtype: PartijType
    periode: RatingPeriode
    partijen: list[Partij]

    @model_validator(mode='after')
    def check_partij_data(self) -> Self:
        # check of de periode een beetje normaal is
        # check of alle data van de partijen een beetje normaal zijn
        if any(self.periode.als_datum() < p.periode.als_datum()
               for p in self.partijen):
            raise ValueError("Datum van partij is na berekendatum.")
        
        # TODO wat doen we met data heel ver in het verleden?

        return self


class RatingResultaat(BaseModel):
    rating: int
    nv_waarde: float
    bron: RatingBron
    periode: RatingPeriode


class PartijBerekening(BaseModel):
    partij: Partij
    speler_rating: RatingResultaat
    tegenstander_rating: RatingResultaat
    wwe: float
    k_waarde: float
    delta: float
    telt_mee: Literal[True] = True


class PartijTeltNietMee(BaseModel):
    partij: Partij
    reden: str
    telt_mee: Literal[False] = False


PartijResultaat = PartijBerekening | PartijTeltNietMee


class LprLimitering(BaseModel):
    lpr: int | None
    ondergrens: int | None
    bovengrens: int | None


class LijstBerekening(BaseModel):
    oude_rating: RatingResultaat
    nieuwe_rating: RatingResultaat
    gespeeld: int
    delta: int
    bonus: int
    lpr: LprLimitering
    partijen: list[PartijResultaat]
