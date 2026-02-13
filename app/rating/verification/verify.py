from enum import Enum
from functools import partial

from dacite import Config, from_dict

from ..domain.models import PartijLijst, Speler
from ..repository import RatingRepository
from .exc import VerificationError
from .models import PartijLijst as PartijLijstIn
from .models import Speler as SpelerIn


def validate_speler(speler: SpelerIn, repo: RatingRepository) -> Speler:
    knsb_id = speler.knsb_id
    fide_id = speler.fide_id

    if knsb_id:
        knsb = repo.get_knsb(knsb_id)
        if not fide_id:
            fide_id = knsb.fide_id
        elif fide_id != knsb.fide_id:
            raise VerificationError(f"Geen match tussen gegeven KNSB ID {knsb_id} en FIDE ID {fide_id}.")
    
    elif fide_id:
        fide = repo.get_fide(fide_id)
        knsb = repo.get_knsb_from_fide(fide_id)
        if knsb:
            knsb_id = knsb.knsb_id
        
    return Speler(knsb_id, fide_id)


def validate_partijlijst(lijst: PartijLijstIn, repo: RatingRepository) -> PartijLijst:
    validate = partial(validate_speler, repo=repo)

    config = Config(cast=[Enum], type_hooks={SpelerIn: validate})
    domain_lijst = from_dict(PartijLijst, lijst.model_dump(), config=config)
    for partij in domain_lijst.partijen:
        if partij.tegenstander == domain_lijst.speler:
            raise VerificationError("Een speler kan niet tegen zichzelf spelen.")
    return domain_lijst
