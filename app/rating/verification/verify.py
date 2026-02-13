from enum import Enum

from dacite import from_dict, Config

from ..domain.models import PartijLijst, Speler
from ..repository import RatingRepository
from .models import PartijLijst as PartijLijstIn
from .exceptions import VerificationError


def validate_speler(speler: Speler, repo: RatingRepository) -> Speler:
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
    domain_lijst = from_dict(PartijLijst, lijst.model_dump(), config=Config(cast=[Enum]))
    domain_lijst.speler = validate_speler(domain_lijst.speler, repo)
    for partij in domain_lijst.partijen:
        partij.tegenstander = validate_speler(partij.tegenstander, repo)
        if partij.tegenstander == domain_lijst.speler:
            raise VerificationError("Een speler kan niet tegen zichzelf spelen.")
    return domain_lijst
