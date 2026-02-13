from ...repository import RatingRepository
from ..models import (LijstBerekening, PartijLijst, PartijType, RatingBron,
                      RatingContext, RatingResultaat)
from .bonus import bereken_ratingbonus
from .geldende_rating import bereken_speler_rating
from .lpr import bereken_lpr, bereken_lpr_limitering, limiteer_door_lpr
from .ratingverandering import bereken_ratingverandering


def bereken_nieuwe_rating(lijst: PartijLijst, repo: RatingRepository):
    lpr = bereken_lpr(lijst, repo)

    resultaten = [
        bereken_ratingverandering(lijst.speler, partij, lijst.partijtype, lpr, repo)
        for partij in lijst.partijen
    ]
    delta = round(sum((r.delta for r in resultaten if r.telt_mee), start=0))  # type: ignore

    # dit is lastig, want wat als deze berekening gebeurt op de eerste van de maand?
    # dan is de huidige periode ook de te berekenen periode
    ctx = RatingContext(lijst.partijtype, lijst.periode, lpr)
    recente_rating = bereken_speler_rating(lijst.speler, ctx, repo)

    nieuwe_rating = recente_rating.rating + delta

    if ctx.partijtype == PartijType.KLASSIEK:
        nieuwe_rating = max(1200, nieuwe_rating)
    else:
        nieuwe_rating = max(400, nieuwe_rating)

    limitering = bereken_lpr_limitering(recente_rating.rating, lpr, delta)
    nieuwe_rating = limiteer_door_lpr(nieuwe_rating, limitering)

    if nieuwe_rating < 1750:
        bonus = min(bereken_ratingbonus(lijst.speler, ctx), 1750 - nieuwe_rating)
        nieuwe_rating += bonus
    else:
        bonus = 0

    gespeeld = len([x for x in resultaten if x.telt_mee])
    nieuwe_nv = min(100, recente_rating.nv_waarde + gespeeld)

    nieuwe_rating_resultaat = RatingResultaat(
        nieuwe_rating, nieuwe_nv, RatingBron.CALC, lijst.periode
    )

    return LijstBerekening(
        recente_rating,
        nieuwe_rating_resultaat,
        gespeeld,
        delta,
        bonus,
        limitering,
        resultaten
    )
