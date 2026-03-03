from ...repository import FideRating, KnsbRating, RatingRepository
from ..exc import PlayerNotFoundError
from ..models import (GameType, Player, RatingContext, RatingResult,
                      RatingSource)
from .tlpr import calculate_tlpr


def calculate_knsb_rating(knsb: KnsbRating, ctx: RatingContext) -> RatingResult | None:
    if ctx.game_type == GameType.RAPID and knsb.rapid_rating:
        return RatingResult(
            knsb.rapid_rating,
            knsb.rapid_games,  # type: ignore
            RatingSource.KR,
            ctx.period
        )
    
    elif ctx.game_type == GameType.BLITZ and knsb.blitz_rating:
        return RatingResult(
            knsb.blitz_rating,
            knsb.blitz_games,  # type: ignore
            RatingSource.KB,
            ctx.period
        )
    
    elif knsb.standard_rating and (
        ctx.game_type == GameType.STANDARD or knsb.standard_rating >= 1300
    ):
        return RatingResult(
            knsb.standard_rating,
            knsb.standard_games,  # type: ignore
            RatingSource.KS,
            ctx.period
        )
    
    
def calculate_fide_rating(fide: FideRating, ctx: RatingContext) -> RatingResult | None:
    if fide.standard_rating:
        return RatingResult(
            fide.standard_rating,
            1000 / fide.standard_k,  # type: ignore
            RatingSource.FS,
            ctx.period
        )
    
    elif ctx.game_type == GameType.RAPID and fide.rapid_rating:
        return RatingResult(
            fide.rapid_rating,
            1000 / fide.rapid_k,  # type: ignore
            RatingSource.FR,
            ctx.period
        )

    if ctx.game_type == GameType.BLITZ and fide.blitz_rating:
        return RatingResult(
            fide.blitz_rating,
            1000 / fide.blitz_k,  # type: ignore
            RatingSource.FB,
            ctx.period
        )


def applicable_fide_rating(player: Player, ctx: RatingContext, repo: RatingRepository) -> RatingResult | None:
    if not player.fide_id:
        return
    
    rating = repo.get_fide_rating(player.fide_id, ctx.period)
    if rating:
        return calculate_fide_rating(rating, ctx)


def applicable_knsb_rating(player: Player, ctx: RatingContext, repo: RatingRepository) -> RatingResult | None:
    if not player.knsb_id:
        return

    rating = repo.get_knsb_rating(player.knsb_id, ctx.period)
    if rating:
        return calculate_knsb_rating(rating, ctx)


def calculate_applicable_rating(
    player: Player,
    ctx: RatingContext,
    repo: RatingRepository,
    for_opponent: bool = False
) -> RatingResult | None:
    
    # We willen de get_fide functie alleen aanroepen als het echt
    # nodig is. Die is namelijk een stuk trager dan get_knsb.
    # Maar nu ziet het er niet echt mooi uit.
    
    if not player.knsb_id:
        return applicable_fide_rating(player, ctx, repo)
    
    knsb_rating = applicable_knsb_rating(player, ctx, repo)
    if not player.fide_id:
        return knsb_rating
    
    if not knsb_rating:
        return applicable_fide_rating(player, ctx, repo)
    
    knsb = repo.get_knsb(player.knsb_id)
    if knsb and knsb.fed == "NED":
        return knsb_rating
    
    if for_opponent:
        fide_rating = applicable_fide_rating(player, ctx, repo)
        if not fide_rating or knsb_rating.rating >= fide_rating.rating:
            return knsb_rating
        return fide_rating
    
    if repo.has_played_game(player.knsb_id):
        return knsb_rating
    
    return applicable_fide_rating(player, ctx, repo)


def calculate_opponent_rating(opponent: Player, ctx: RatingContext, repo: RatingRepository) -> RatingResult | None:
    applicable_rating = calculate_applicable_rating(opponent, ctx, repo, for_opponent=True)
    if applicable_rating:
        return applicable_rating

    if ctx.game_type == GameType.STANDARD:
        return
    
    return calculate_tlpr(opponent, ctx, repo)


def calculate_player_rating(player: Player, ctx: RatingContext, repo: RatingRepository) -> RatingResult:
    applicable_rating = calculate_applicable_rating(player, ctx, repo)
    if applicable_rating:
        return applicable_rating
    
    if ctx.lpr is None:
        raise PlayerNotFoundError("Kon oude rating niet calculate voor player: "
                                  "geen applicable rating en geen LPR.")
    
    return RatingResult(ctx.lpr, 1, RatingSource.LPR, ctx.period)
