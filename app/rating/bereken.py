from .domein import BerekeningsResultaat, Partij, PartijType, RatingContext
from .regels import (bepaal_ratingbonus, bepaal_speler_rating, bereken_lpr,
                     bereken_ratingverandering, limiteer_door_lpr)
from .speler import Speler
from .exceptions import RatingError

def bereken_nieuwe_rating(
    speler: Speler,
    ctx: RatingContext,
    partijen: list[Partij]
):
    
    # werkt ook als de partijen list leeg is
    if not all(p.ctx.partijtype == partijen[0].ctx.partijtype for p in partijen):
        raise RatingError("Alle partijen moeten dezelfde partijtype hebben!")
    
    if not all(p.speler == speler for p in partijen):
        raise RatingError("Alle partijen moeten dezelfde speler hebben!")

    lpr = bereken_lpr(partijen)

    resultaten = []
    for partij in partijen:
        if lpr:
            partij.ctx.lpr = lpr.rating
        resultaten.append(bereken_ratingverandering(partij))
    delta = round(sum((r.delta for r in resultaten if r), start=0))

    # dit is lastig, want wat als deze berekening gebeurt op de eerste van de maand?
    # dan is de huidige periode ook de te berekenen periode
    if not ctx.lpr and lpr:
        ctx.lpr = lpr.rating
    recente_rating = bepaal_speler_rating(speler, ctx)

    nieuwe_rating = recente_rating.rating + delta

    if ctx.partijtype == PartijType.KLASSIEK:
        nieuwe_rating = max(1200, nieuwe_rating)
    else:
        nieuwe_rating = max(400, nieuwe_rating)
    
    if lpr:
        nieuwe_rating = limiteer_door_lpr(nieuwe_rating, recente_rating.rating, lpr.rating, delta)

    if nieuwe_rating < 1750:
        bonus = min(bepaal_ratingbonus(speler, ctx), 1750 - nieuwe_rating)
        nieuwe_rating += bonus
    else:
        bonus = 0

    return BerekeningsResultaat(
        nieuwe_rating,
        recente_rating,
        resultaten,
        delta,
        bonus,
        lpr.rating if lpr else None
    )
