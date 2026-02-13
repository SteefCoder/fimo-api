from ...repository import FideRating, KnsbRating, RatingRepository
from ..exceptions import PlayerNotFoundError
from ..models import (PartijType, RatingBron, RatingContext, RatingResultaat,
                      Speler)
from .tlpr import bereken_tlpr


def bereken_knsb_rating(knsb: KnsbRating, ctx: RatingContext) -> RatingResultaat | None:
    if ctx.partijtype == PartijType.RAPID and knsb.rapid_rating:
        return RatingResultaat(
            knsb.rapid_rating,
            knsb.rapid_games,  # type: ignore
            RatingBron.KR,
            ctx.periode
        )
    
    elif ctx.partijtype == PartijType.BLITZ and knsb.blitz_rating:
        return RatingResultaat(
            knsb.blitz_rating,
            knsb.blitz_games,  # type: ignore
            RatingBron.KB,
            ctx.periode
        )
    
    elif knsb.standard_rating and (
        ctx.partijtype == PartijType.KLASSIEK or knsb.standard_rating >= 1300
    ):
        return RatingResultaat(
            knsb.standard_rating,
            knsb.standard_games,  # type: ignore
            RatingBron.KS,
            ctx.periode
        )
    
    
def bereken_fide_rating(fide: FideRating, ctx: RatingContext) -> RatingResultaat | None:
    if fide.standard_rating:
        return RatingResultaat(
            fide.standard_rating,
            1000 / fide.standard_k,  # type: ignore
            RatingBron.FS,
            ctx.periode
        )
    
    elif ctx.partijtype == PartijType.RAPID and fide.rapid_rating:
        return RatingResultaat(
            fide.rapid_rating,
            1000 / fide.rapid_k,  # type: ignore
            RatingBron.FR,
            ctx.periode
        )

    if ctx.partijtype == PartijType.BLITZ and fide.blitz_rating:
        return RatingResultaat(
            fide.blitz_rating,
            1000 / fide.blitz_k,  # type: ignore
            RatingBron.FB,
            ctx.periode
        )


def geldende_fide_rating(speler: Speler, ctx: RatingContext, repo: RatingRepository) -> RatingResultaat | None:
    if not speler.fide_id:
        return
    
    rating = repo.get_fide_rating(speler.fide_id, ctx.periode)
    if rating:
        return bereken_fide_rating(rating, ctx)


def geldende_knsb_rating(speler: Speler, ctx: RatingContext, repo: RatingRepository) -> RatingResultaat | None:
    if not speler.knsb_id:
        return

    rating = repo.get_knsb_rating(speler.knsb_id, ctx.periode)
    if rating:
        return bereken_knsb_rating(rating, ctx)


def bereken_geldende_rating(
    speler: Speler,
    ctx: RatingContext,
    repo: RatingRepository,
    voor_tegenstander: bool = False
) -> RatingResultaat | None:
    
    # We willen de get_fide functie alleen aanroepen als het echt
    # nodig is. Die is namelijk een stuk trager dan get_knsb.
    # Maar nu ziet het er niet echt mooi uit.
    
    if not speler.knsb_id:
        return geldende_fide_rating(speler, ctx, repo)
    
    knsb_rating = geldende_knsb_rating(speler, ctx, repo)
    if not speler.fide_id:
        return knsb_rating
    
    if not knsb_rating:
        return geldende_fide_rating(speler, ctx, repo)
    
    knsb = repo.get_knsb(speler.knsb_id)
    if knsb and knsb.fed == "NED":
        return knsb_rating
    
    if voor_tegenstander:
        fide_rating = geldende_fide_rating(speler, ctx, repo)
        if not fide_rating or knsb_rating.rating >= fide_rating.rating:
            return knsb_rating
        return fide_rating
    
    if repo.heeft_partij_gespeeld(speler.knsb_id):
        return knsb_rating
    
    return geldende_fide_rating(speler, ctx, repo)


def bereken_tegenstander_rating(tegenstander: Speler, ctx: RatingContext, repo: RatingRepository) -> RatingResultaat | None:
    geldende_rating = bereken_geldende_rating(tegenstander, ctx, repo, voor_tegenstander=True)
    if geldende_rating:
        return geldende_rating

    if ctx.partijtype == PartijType.KLASSIEK:
        return
    
    return bereken_tlpr(tegenstander, ctx, repo)


def bereken_speler_rating(speler: Speler, ctx: RatingContext, repo: RatingRepository) -> RatingResultaat:
    geldende_rating = bereken_geldende_rating(speler, ctx, repo)
    if geldende_rating:
        return geldende_rating
    
    if ctx.lpr is None:
        raise PlayerNotFoundError("Kon oude rating niet bereken voor speler: "
                                  "geen geldende rating en geen LPR.")
    
    return RatingResultaat(ctx.lpr, 1, RatingBron.LPR, ctx.periode)
