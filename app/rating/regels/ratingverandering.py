import math

from ..domein import Partij, PartijResultaat
from .geldende_rating import bepaal_speler_rating, bepaal_tegenstander_rating
from .k_factor import bereken_k


def bereken_we(rv: int) -> float:
    """Implementatie van 2.8 (verwachte score We)."""
    return 1/2 + math.erf(7*rv/(2000*math.sqrt(2)))/2


def bereken_ratingverandering(partij: Partij) -> PartijResultaat | None:
    tegenstander = bepaal_tegenstander_rating(partij.tegenstander, partij.ctx)
    if not tegenstander:
        return
    
    speler = bepaal_speler_rating(partij.speler, partij.ctx)

    k = bereken_k(partij.speler, speler)
    we = bereken_we(speler.rating - tegenstander.rating)
    
    wwe = partij.resultaat.value - we
    delta = k * (partij.resultaat.value - we)
    
    return PartijResultaat(speler, tegenstander, wwe, k, delta)
