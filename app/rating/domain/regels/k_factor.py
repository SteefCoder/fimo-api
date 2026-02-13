import math

from ...repository import RatingRepository
from ..models import Partij, RatingResultaat, Resultaat, Speler
from .util import is_jeugd


def bereken_k_jeugd(rating: int, nv: float) -> float:
    if nv < 30:
        return 216 / math.sqrt(nv)
    
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


def bereken_k(speler: Speler, rating: RatingResultaat, repo: RatingRepository) -> float:
    if is_jeugd(speler, rating.periode, repo):
        return bereken_k_jeugd(rating.rating, rating.nv_waarde)
    return bereken_k_senior(rating.rating, rating.nv_waarde)


def k_wordt_gehalveerd(
    speler: Speler,
    partij: Partij,
    tegenstander_nv: float,
    wwe: float,
    repo: RatingRepository
) -> bool:
    return (
        tegenstander_nv < 100 and
        wwe < 0 and
        partij.resultaat == Resultaat.VERLIES and
        not is_jeugd(speler, partij.periode, repo) and
        is_jeugd(partij.tegenstander, partij.periode, repo)
    )
