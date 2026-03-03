import math

from ...repository import RatingRepository
from ..models import (Game, GameCalculation, GameDoesNotCount, GameResult,
                      GameType, Player, RatingContext)
from .applicable_rating import (calculate_opponent_rating,
                                calculate_player_rating)
from .k_factor import calculate_k, k_is_halved


def calculate_we(rv: int) -> float:
    """Implementatie van 2.8 (verwachte score We)."""
    return 1/2 + math.erf(7*rv/(2000*math.sqrt(2)))/2


def calculate_rating_change(
    player: Player,
    game: Game,
    game_type: GameType,
    lpr: int | None,
    repo: RatingRepository
) -> GameResult:
    
    ctx = RatingContext(game_type, game.period, lpr)
    opponent_rating = calculate_opponent_rating(game.opponent, ctx, repo)
    if not opponent_rating:
        return GameDoesNotCount(game, "Kon de rating van de tegenstander niet bepalen.")
    
    player_rating = calculate_player_rating(player, ctx, repo)

    we = calculate_we(player_rating.rating - opponent_rating.rating)
    wwe = game.result.value - we

    k_factor = calculate_k(player, player_rating, repo)
    if k_is_halved(player, game, opponent_rating.nv_value, wwe, repo):
        k_factor /= 2

    delta = k_factor * wwe
    
    return GameCalculation(
        game,
        player_rating,
        opponent_rating,
        wwe,
        k_factor,
        delta
    )
