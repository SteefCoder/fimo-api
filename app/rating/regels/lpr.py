import math

from ..domein import Flag, Partij, RatingBron, RatingResultaat
from ..periode import RatingPeriode
from ..speler import Speler
from .geldende_rating import bepaal_tegenstander_rating, bepaal_geldende_rating


def bereken_lpr(partijen: list[Partij]) -> RatingResultaat | None:
    ratings = []
    scores = []
    for partij in partijen:
        rating = bepaal_tegenstander_rating(partij.tegenstander, partij.ctx)
        if rating is None:
            continue

        ratings.append(rating.rating)
        scores.append(partij.resultaat.value)

    if len(ratings) == 0:
        return

    rct = sum(ratings) / len(ratings)
    if sum(scores) == 0 or sum(scores) == len(scores):
        scores += [0.5]

        # dit moet eigenlijk de rating van de speler zijn
        # maar ik weet niet op welke datum ik die moet pakken
        # en ook niet wat er gebeurt als de speler geen geldende rating heeft
        ratings += [rct]

    wt = sum(scores)
    nt = len(scores)
    x = rct + 400 * (2*wt/nt - 1)
    for _ in range(4):
        z = [7*(x - r)/(2000 * math.sqrt(2)) for r in ratings]
        S = wt - nt/2 - sum(math.erf(i) for i in z)/2
        Sp = - 7/(2000*math.sqrt(2*math.pi)) * sum(math.exp(-i**2) for i in z)
        x -= S / Sp

    bron = RatingBron(Flag.LPR, RatingPeriode.huidige_periode())
    return RatingResultaat(round(x), 1, bron)


def limiteer_door_lpr(nieuwe_rating: int, recente_rating: int, lpr: int, delta: int) -> int:
    if delta > 0 and recente_rating < lpr:
        return min(lpr + 20, nieuwe_rating)
    
    if delta < 0 and recente_rating > lpr:
        return max(lpr - 20, nieuwe_rating)
    
    if delta != 0 and recente_rating == lpr:
        return max(lpr - 20, min(lpr + 20, nieuwe_rating))
    
    return nieuwe_rating
