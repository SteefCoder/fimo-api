import datetime
import math

from ..domein import RatingResultaat
from ..periode import RatingPeriode
from ..speler import Speler


def is_jeugd(speler: Speler, periode: RatingPeriode) -> bool:
    if speler.knsb and periode.jaar - speler.knsb.birthyear <= 18:
        return True
    
    return speler.fide is not None and periode.jaar - speler.fide.birthyear <= 18


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


def bereken_k(speler: Speler, resultaat: RatingResultaat) -> float:
    if is_jeugd(speler, resultaat.bron.periode):
        return bereken_k_jeugd(resultaat.rating, resultaat.nv_waarde)
    return bereken_k_senior(resultaat.rating, resultaat.nv_waarde)
