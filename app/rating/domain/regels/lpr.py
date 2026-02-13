import math

from ...repository import RatingRepository
from ..models import LprLimitering, PartijLijst, RatingContext
from .geldende_rating import (bereken_geldende_rating,
                              bereken_tegenstander_rating)


def geldende_tegenstander_ratings(lijst: PartijLijst, repo: RatingRepository) -> tuple[list[int], list[float]]:
    ratings = []
    scores = []
    for partij in lijst.partijen:
        ctx = RatingContext(lijst.partijtype, partij.periode)
        rating = bereken_tegenstander_rating(partij.tegenstander, ctx, repo)
        if rating is None:
            continue

        ratings.append(rating.rating)
        scores.append(partij.resultaat.value)

    return ratings, scores


def bereken_lpr(lijst: PartijLijst, repo: RatingRepository) -> int | None:
    ratings, scores = geldende_tegenstander_ratings(lijst, repo)
    if len(ratings) == 0:
        return
    
    wt = sum(scores)
    nt = len(scores)
    rct = sum(ratings) / nt
    
    if sum(scores) == 0 or sum(scores) == len(scores):
        scores += [0.5]

        # ik gok maar dat de rct gebruikt moet worden als
        # de speler geen geldende rating heeft.
        ctx = RatingContext(lijst.partijtype, lijst.periode)
        speler_rating = bereken_geldende_rating(lijst.speler, ctx, repo)
        ratings += [speler_rating.rating if speler_rating else rct]

    lpr = rct + 400 * (2*wt/nt - 1)
    for _ in range(4):
        z = [7*(lpr - r)/(2000 * math.sqrt(2)) for r in ratings]
        S = wt - nt/2 - sum(math.erf(i) for i in z)/2
        Sp = - 7/(2000*math.sqrt(2*math.pi)) * sum(math.exp(-i**2) for i in z)
        lpr -= S / Sp

    return round(lpr)


def bereken_lpr_limitering(recente_rating: int, lpr: int | None, delta: int) -> LprLimitering:
    if not lpr:
        return LprLimitering(None, None, None)
    
    ondergrens = None
    bovengrens = None

    if delta > 0 and recente_rating < lpr:
        bovengrens = lpr + 20
    elif delta < 0 and recente_rating > lpr:
        ondergrens = lpr - 20
    elif delta != 0 and recente_rating == lpr:
        ondergrens = lpr - 20
        bovengrens = lpr + 20
    
    return LprLimitering(lpr, ondergrens, bovengrens)


def limiteer_door_lpr(nieuwe_rating: int, limitering: LprLimitering) -> int:
    if limitering.ondergrens:
        nieuwe_rating = max(limitering.ondergrens, nieuwe_rating)
    if limitering.bovengrens:
        nieuwe_rating = min(limitering.bovengrens, nieuwe_rating)
    return nieuwe_rating
