import math

from ...repository import RatingRepository
from ..models import (Partij, PartijBerekening, PartijResultaat,
                      PartijTeltNietMee, PartijType, RatingContext, Speler)
from .geldende_rating import bereken_speler_rating, bereken_tegenstander_rating
from .k_factor import bereken_k, k_wordt_gehalveerd


def bereken_we(rv: int) -> float:
    """Implementatie van 2.8 (verwachte score We)."""
    return 1/2 + math.erf(7*rv/(2000*math.sqrt(2)))/2


def bereken_ratingverandering(
    speler: Speler,
    partij: Partij,
    partijtype: PartijType,
    lpr: int | None,
    repo: RatingRepository
) -> PartijResultaat:
    
    ctx = RatingContext(partijtype, partij.periode, lpr)
    tegenstander_rating = bereken_tegenstander_rating(partij.tegenstander, ctx, repo)
    if not tegenstander_rating:
        return PartijTeltNietMee(partij, "Kon de rating van de tegenstander niet bepalen.")
    
    speler_rating = bereken_speler_rating(speler, ctx, repo)

    we = bereken_we(speler_rating.rating - tegenstander_rating.rating)
    wwe = partij.resultaat.value - we

    k_factor = bereken_k(speler, speler_rating, repo)
    if k_wordt_gehalveerd(speler, partij, tegenstander_rating.nv_waarde, wwe, repo):
        k_factor /= 2

    delta = k_factor * wwe
    
    return PartijBerekening(
        partij,
        speler_rating,
        tegenstander_rating,
        wwe,
        k_factor,
        delta
    )
