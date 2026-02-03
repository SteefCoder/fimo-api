from ..domein import Flag, PartijType, RatingBron, RatingContext, RatingResultaat
from app.models import FideRating, KnsbRating
from ..speler import Speler


def bepaal_knsb_rating(knsb: KnsbRating | None, ctx: RatingContext) -> RatingResultaat | None:
    """Deelimplementatie van 2.2.1, 2.2.2 en 2.2.3 (protocol geldende rating)"""
    if knsb is None:
        return

    if ctx.partijtype == PartijType.RAPID and knsb.rapid_rating is not None:
        bron = RatingBron(Flag.KR, ctx.periode)
        return RatingResultaat(knsb.rapid_rating, knsb.rapid_games, bron)
    
    if ctx.partijtype == PartijType.BLITZ and knsb.blitz_rating is not None:
        bron = RatingBron(Flag.KB, ctx.periode)
        return RatingResultaat(knsb.blitz_rating, knsb.blitz_games, bron)
    
    if knsb.standard_rating  is not None and (
        ctx.partijtype == PartijType.KLASSIEK or knsb.standard_rating >= 1300
    ):
        bron = RatingBron(Flag.KS, ctx.periode)
        return RatingResultaat(knsb.standard_rating, knsb.standard_games, bron)
    

def bepaal_fide_rating(fide: FideRating | None, ctx: RatingContext) -> RatingResultaat | None:
    """Deelimplementatie van 2.2.1, 2.2.2 en 2.2.3
    protocol geldende rating"""
    if fide is None:
        return
    
    if fide.standard_rating is not None:
        bron = RatingBron(Flag.FS, ctx.periode)
        return RatingResultaat(
            fide.standard_rating,
            1000 / fide.standard_k,
            bron
        )
    
    if ctx.partijtype == PartijType.RAPID and fide.rapid_rating is not None:
        bron = RatingBron(Flag.FR, ctx.periode)
        return RatingResultaat(
            fide.rapid_rating,
            1000 / fide.rapid_k,
            bron
        )

    if ctx.partijtype == PartijType.BLITZ and fide.blitz_rating is not None:
        bron = RatingBron(Flag.FB, ctx.periode)
        return RatingResultaat(
            fide.blitz_rating,
            1000 / fide.blitz_k,
            bron
        )


def bepaal_geldende_rating(
    speler: Speler,
    ctx: RatingContext,
    voor_tegenstander: bool = False
) -> RatingResultaat | None:
    
    knsb = bepaal_knsb_rating(speler.get_knsb_rating(ctx.periode), ctx)
    fide = bepaal_fide_rating(speler.get_fide_rating(ctx.periode), ctx)

    if knsb is None:
        return fide
    
    if fide is None:
        return knsb
    
    if speler.knsb and speler.knsb.fed == "NED":
        return knsb
    
    if voor_tegenstander:
        return knsb if knsb.rating >= fide.rating else fide
    
    return knsb if speler.heeft_partij_gespeeld() else fide


def bepaal_tegenstander_rating(tegenstander: Speler, ctx: RatingContext) -> RatingResultaat | None:
    geldende_rating = bepaal_geldende_rating(tegenstander, ctx, voor_tegenstander=True)
    if geldende_rating:
        return geldende_rating

    if ctx.partijtype == PartijType.KLASSIEK:
        return
    
    # bereken de tlpr
    

def bepaal_speler_rating(speler: Speler, ctx: RatingContext) -> RatingResultaat:
    geldende_rating = bepaal_geldende_rating(speler, ctx)
    if geldende_rating:
        return geldende_rating
    
    if ctx.lpr is None:
        raise ValueError("Verwachtte LPR voor het berekenen van R0!")
    
    bron = RatingBron(Flag.LPR, ctx.periode)
    return RatingResultaat(ctx.lpr, 1, bron)
