from .models import PartijLijst, LijstBerekening
from ..repository import RatingRepository
from ..domain.regels import bereken
from .verify import validate_partijlijst

from dataclasses import asdict


def bereken_nieuwe_rating(lijst: PartijLijst, repo: RatingRepository) -> LijstBerekening:
    domain_lijst = validate_partijlijst(lijst, repo)
    berekening = bereken.bereken_nieuwe_rating(domain_lijst, repo)
    return LijstBerekening.model_validate(asdict(berekening))
