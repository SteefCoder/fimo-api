from ...repository import RatingRepository
from ..exc import PlayerNotFoundError
from ..models import RatingPeriode, Speler


def is_jeugd(speler: Speler, periode: RatingPeriode, repo: RatingRepository) -> bool:
    if speler.knsb_id:
        knsb = repo.get_knsb(speler.knsb_id)
        leeftijd = periode.jaar - knsb.birthyear
        return leeftijd <= 18
    
    elif speler.fide_id:
        fide = repo.get_fide(speler.fide_id)
        leeftijd = periode.jaar - fide.birthyear
        return leeftijd <= 18

    # hmm hier kunnen we niks mee
    raise PlayerNotFoundError("Speler heeft geen fide en geen knsb???")
