import math

from ...repository import RatingRepository
from ..models import Game, Player, RatingResult, Result
from .util import is_junior


def calculate_k_junior(rating: int, nv: float) -> float:
    if nv < 30:
        return 216 / math.sqrt(nv)
    
    if rating <= 2100:
        return 40
    elif 2100 < rating < 2400:
        return 25 - (rating - 2100) / 10
    else:
        return 10


def calculate_k_senior(rating: int, nv: float) -> float:
    if nv < 75:
        return 216 / math.sqrt(nv)
    
    if rating <= 2100:
        return 25
    elif 2100 < rating < 2400:
        return 25 - (rating - 2100) / 20
    else:
        return 10


def calculate_k(player: Player, rating: RatingResult, repo: RatingRepository) -> float:
    if is_junior(player, rating.period, repo):
        return calculate_k_junior(rating.rating, rating.nv_value)
    return calculate_k_senior(rating.rating, rating.nv_value)


def k_is_halved(
    player: Player,
    game: Game,
    opponent_nv: float,
    wwe: float,
    repo: RatingRepository
) -> bool:
    return (
        opponent_nv < 100 and
        wwe < 0 and
        not is_junior(player, game.period, repo) and
        is_junior(game.opponent, game.period, repo)
    )
