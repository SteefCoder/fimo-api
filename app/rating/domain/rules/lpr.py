import math

from ...repository import RatingRepository
from ..models import GameList, LprLimitation, RatingContext
from .applicable_rating import (calculate_applicable_rating,
                                calculate_opponent_rating)


def applicable_opponent_ratings(game_list: GameList, repo: RatingRepository) -> tuple[list[int], list[float]]:
    ratings = []
    scores = []
    for game in game_list.games:
        ctx = RatingContext(game_list.game_type, game.period)
        rating = calculate_opponent_rating(game.opponent, ctx, repo)
        if rating is None:
            continue

        ratings.append(rating.rating)
        scores.append(game.result.value)

    return ratings, scores


def calculate_lpr(game_list: GameList, repo: RatingRepository) -> int | None:
    ratings, scores = applicable_opponent_ratings(game_list, repo)
    if len(ratings) == 0:
        return
    
    wt = sum(scores)
    nt = len(scores)
    rct = sum(ratings) / nt
    
    if sum(scores) == 0 or sum(scores) == len(scores):
        scores += [0.5]

        # ik gok maar dat de rct gebruikt moet worden als
        # de speler geen geldende rating heeft.
        ctx = RatingContext(game_list.game_type, game_list.period)
        speler_rating = calculate_applicable_rating(game_list.player, ctx, repo)
        ratings += [speler_rating.rating if speler_rating else rct]

    lpr = rct + 400 * (2*wt/nt - 1)
    for _ in range(4):
        z = [7*(lpr - r)/(2000 * math.sqrt(2)) for r in ratings]
        S = wt - nt/2 - sum(math.erf(i) for i in z)/2
        Sp = - 7/(2000*math.sqrt(2*math.pi)) * sum(math.exp(-i**2) for i in z)
        lpr -= S / Sp

    return round(lpr)


def calculate_lpr_limitation(recent_rating: int, lpr: int | None, delta: int) -> LprLimitation:
    if not lpr:
        return LprLimitation(None, None, None)
    
    lower_limit = None
    upper_limit = None

    if delta > 0 and recent_rating < lpr:
        upper_limit = lpr + 20
    elif delta < 0 and recent_rating > lpr:
        lower_limit = lpr - 20
    elif delta != 0 and recent_rating == lpr:
        lower_limit = lpr - 20
        upper_limit = lpr + 20
    
    return LprLimitation(lpr, lower_limit, upper_limit)


def limit_by_lpr(new_rating: int, limitation: LprLimitation) -> int:
    if limitation.lower_limit:
        new_rating = max(limitation.lower_limit, new_rating)
    if limitation.upper_limit:
        new_rating = min(limitation.upper_limit, new_rating)
    return new_rating
