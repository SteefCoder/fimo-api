from ...repository import RatingRepository
from ..models import (GameList, GameType, ListCalculation, RatingContext,
                      RatingResult, RatingSource)
from .applicable_rating import calculate_player_rating
from .bonus import calculate_rating_bonus
from .lpr import calculate_lpr, calculate_lpr_limitation, limit_by_lpr
from .rating_change import calculate_rating_change


def calculate_new_rating(game_list: GameList, repo: RatingRepository):
    lpr = calculate_lpr(game_list, repo)

    results = [
        calculate_rating_change(game_list.player, game, game_list.game_type, lpr, repo)
        for game in game_list.games
    ]
    delta = round(sum((r.delta for r in results if r.counts), start=0))  # type: ignore

    # dit is lastig, want wat als deze calculateing gebeurt op de eerste van de maand?
    # dan is de huidige periode ook de te calculateen periode
    ctx = RatingContext(game_list.game_type, game_list.period, lpr)
    recent_rating = calculate_player_rating(game_list.player, ctx, repo)

    new_rating = recent_rating.rating + delta

    if ctx.game_type == GameType.STANDARD:
        new_rating = max(1200, new_rating)
    else:
        new_rating = max(400, new_rating)

    limitation = calculate_lpr_limitation(recent_rating.rating, lpr, delta)
    new_rating = limit_by_lpr(new_rating, limitation)

    if new_rating < 1750:
        bonus = min(calculate_rating_bonus(game_list.player, ctx), 1750 - new_rating)
        new_rating += bonus
    else:
        bonus = 0

    played = len([x for x in results if x.counts])
    new_nv = min(100, recent_rating.nv_value + played)

    nieuwe_rating_resultaat = RatingResult(
        new_rating, new_nv, RatingSource.CALC, game_list.period
    )

    return ListCalculation(
        recent_rating,
        nieuwe_rating_resultaat,
        played,
        delta,
        bonus,
        limitation,
        results
    )
