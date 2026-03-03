from ...repository import RatingRepository
from ..exc import PlayerNotFoundError
from ..models import Player, RatingPeriod


def is_junior(player: Player, period: RatingPeriod, repo: RatingRepository) -> bool:
    if player.knsb_id:
        knsb = repo.get_knsb(player.knsb_id)
        age = period.year - knsb.birthyear
        return age <= 18
    
    elif player.fide_id:
        fide = repo.get_fide(player.fide_id)
        age = period.year - fide.birthyear
        return age <= 18

    # hmm hier kunnen we niks mee
    raise PlayerNotFoundError("Player heeft geen fide en geen knsb???")
