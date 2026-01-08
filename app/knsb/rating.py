import datetime
from enum import Enum, auto
import pathlib
import sys
import math
import time

sys.path.append(str(pathlib.Path.cwd()))


from app.models import db, KnsbPlayer, KnsbRating, FideRating, FidePlayer
from app import create_app

from sqlalchemy import select
from dataclasses import dataclass


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
    Rl = auto()     # rating van de laatste ratinglijst ipv die van de berekeningsdatum
    Rs = auto()
    LPR = auto()


class Speler:
    """Een speler die vooral dingen doet die met databases te maken hebben."""
    def __init__(self, knsb_id: int | None = None, fide_id: int | None = None) -> None:
        assert knsb_id or fide_id

        self.knsb_id = knsb_id
        self.fide_id = fide_id

        self._knsb = None
        self._fide = None

        if not fide_id and self.knsb:
            self.fide_id = self.knsb.fide_id

    @property
    def knsb(self) -> KnsbPlayer | None:
        if self._knsb:
            return self._knsb
        
        if self.knsb_id:
            query = select(KnsbPlayer).where(KnsbPlayer.knsb_id == self.knsb_id)
            self._knsb = db.session.execute(query).scalar_one()
            return self._knsb
        
    @property
    def fide(self) -> FidePlayer | None:
        if self._fide:
            return self._fide
        
        if self.fide_id:
            query = select(FidePlayer).where(FidePlayer.fide_id == self.fide_id)
            self._fide = db.session.execute(query).scalar_one()
            return self._fide

    def heeft_partij_gespeeld(self) -> bool:
        """Check of de speler in de afgelopen twee jaar een partij heeft
        gespeeld die meetelt voor KNSB-rating. Deze functie kunnen we nog niet implementeren.
        We gaan er nu van uit dat dat wel het geval is als de speler een knsb-id heeft."""
        return self.knsb_id is not None

    def get_knsb_rating(self, datum: datetime.date) -> KnsbRating | None:
        if self.knsb_id is None:
            return None
        
        datum = datum.replace(day=1)
        query = select(KnsbRating).where(KnsbRating.knsb_id == self.knsb_id, KnsbRating.date == datum)
        return db.session.execute(query).scalar()

    def get_fide_rating(self, datum: datetime.date) -> FideRating | None:
        if self.fide_id is None:
            return None
        
        datum = datum.replace(day=1)
        query = select(FideRating).where(FideRating.fide_id == self.fide_id, FideRating.date == datum)
        return db.session.execute(query).scalar()


@dataclass
class Partij:
    speler: Speler
    tegenstander: Speler
    resultaat: Resultaat
    berekeningsdatum: datetime.date
    partijtype: PartijType = PartijType.KLASSIEK


def geldende_knsb_rating(knsb: KnsbRating | None, partijtype: PartijType) -> tuple[int, int, Flag] | None:
    if knsb is None:
        return None
    
    if partijtype == PartijType.RAPID and knsb.rapid_rating is not None:
        return knsb.rapid_rating, knsb.rapid_games, Flag.KR
    
    elif partijtype == PartijType.BLITZ and knsb.blitz_rating is not None:
        return knsb.blitz_rating, knsb.blitz_games, Flag.KB
    
    elif knsb.standard_rating is not None and (partijtype == PartijType.KLASSIEK or knsb.standard_rating >= 1300):
        return knsb.standard_rating, knsb.standard_games, Flag.KS
    
    return None


def geldende_fide_rating(fide: FideRating | None, partijtype: PartijType) -> tuple[int, float, Flag] | None:
    if fide is None:
        return None
    
    if fide.standard_rating is not None:
        return fide.standard_rating, 1000 / fide.standard_k, Flag.FS
    
    if partijtype == PartijType.RAPID and fide.rapid_rating is not None:
        return fide.rapid_rating, 1000 / fide.rapid_k, Flag.FR
    
    elif partijtype == PartijType.BLITZ and fide.blitz_rating is not None:
        return fide.blitz_rating, 1000 / fide.blitz_k, Flag.FB
    
    return None
    

def geldende_rating(speler: Speler, datum: datetime.date, partijtype: PartijType) -> tuple[int, float, Flag] | None:
    knsb_rating = geldende_knsb_rating(speler.get_knsb_rating(datum), partijtype)

    if knsb_rating is not None and (
        (speler.knsb and speler.knsb.fed == "NED") or
        speler.heeft_partij_gespeeld()
    ): return knsb_rating
    
    return geldende_fide_rating(speler.get_fide_rating(datum), partijtype)


def speler_geldende_rating(speler: Speler, datum: datetime.date, partijtype: PartijType):
    res = geldende_rating(speler, datum, partijtype)
    if res:
        rating, nv, flag = res
        return rating, nv, [flag]
    
    res = geldende_rating(speler, datetime.date.today(), partijtype)
    if res:
        rating, nv, flag = res
        return rating, nv, [flag, Flag.Rl, Flag.Rs]


def is_jeugd(speler: Speler, datum: datetime.date) -> bool:
    if speler.knsb and datum.year - speler.knsb.birthyear <= 18:
        return True
    elif speler.fide and datum.year - speler.fide.birthyear <= 18:
        return True
    return False


def bereken_lpr(partijen: list[Partij]) -> float:
    ratings = []
    scores = []
    for p in partijen:
        rating = geldende_rating(p.tegenstander, p.berekeningsdatum, p.partijtype)
        if not rating:
            continue
        ratings.append(rating[0])
        scores.append(p.resultaat.value)

    rct = sum(ratings) / len(ratings)
    if sum(scores) == 0 or sum(scores) == len(scores):
        scores += [0.5]
        ratings += [rct]  # dit moet eigenlijk de rating van de speler zijn

    wt = sum(scores)
    nt = len(scores)
    x = rct + 400 * (2*wt/nt - 1)
    for _ in range(4):
        z = [7*(x - r)/4000 for r in ratings]
        S = wt - nt/2 - sum(math.erf(i) for i in z)/2
        Sp = - 7/(4000*math.sqrt(math.pi)) * sum(math.exp(-i**2) for i in z)
        x -= S / Sp
    return x


def bereken_k_jeugd(rating: int, nv: float) -> float:
    if nv < 30:
        return 216 / math.sqrt(rating)
    
    if rating <= 2100:
        return 40
    elif 2100 < rating < 2400:
        return 25 - (rating - 2100) / 10
    else:
        return 10


def bereken_k_senior(rating: int, nv: float) -> float:
    if nv < 75:
        return 216 / math.sqrt(nv)
    
    if rating <= 2100:
        return 25
    elif 2100 < rating < 2400:
        return 25 - (rating - 2100) / 20
    else:
        return 10
    

def bereken_we(rv: int) -> float:
    return 1/2 + math.erf(7*rv/4000)/2


def bereken_totale_ratingverandering(speler: Speler, partijen: list[Partij]) -> float:
    partijtype = partijen[0].partijtype
    lpr = bereken_lpr(partijen)
    rtt = 0.0

    for partij in partijen:
        assert partij.partijtype == partijtype
        assert partij.speler == speler

        tegenstander_rating = geldende_rating(partij.tegenstander, partij.berekeningsdatum, partijtype)
        if tegenstander_rating:
            tegenstander_rating, _, tflags = tegenstander_rating
        else:
            continue

        speler_rating = speler_geldende_rating(speler, partij.berekeningsdatum, partijtype)
        if speler_rating:
            speler_rating, nv, flags = speler_rating
        else:
            speler_rating, nv, flags = round(lpr), 1, [Flag.Rs, Flag.LPR]


        if is_jeugd(speler, partij.berekeningsdatum):
            k = bereken_k_jeugd(speler_rating, nv)
        else:
            k = bereken_k_senior(speler_rating, nv)
        
        we = bereken_we(speler_rating - tegenstander_rating)
        rtt += k * (partij.resultaat.value - we)

        print(tegenstander_rating, tflags, partij.resultaat.value - we, k * (partij.resultaat.value - we))
    
    return rtt

def test():
    vandaag = datetime.date.today()
    start = time.time()

    s = Speler(knsb_id=8789033)
    partijen = [
        Partij(s, Speler(8313910), Resultaat.REMISE, vandaag, PartijType.RAPID),
        Partij(s, Speler(8547638), Resultaat.WINST, vandaag, PartijType.RAPID),
        Partij(s, Speler(fide_id=100013), Resultaat.VERLIES, vandaag, PartijType.RAPID)
    ]
    print(bereken_totale_ratingverandering(s, partijen))
    
    end = time.time()
    print(f"Did it all in {end - start:.2f}s")


def main():
    app = create_app()
    with app.app_context():
        test()

main()