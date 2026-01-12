from functools import cache, cached_property

from periode import RatingPeriode
from sqlalchemy import select

from app.models import FidePlayer, FideRating, KnsbPlayer, KnsbRating, db


class Speler:
    """Een speler die vooral dingen doet die met databases te maken hebben."""
    def __init__(self, knsb_id: int | None = None, fide_id: int | None = None) -> None:
        assert knsb_id or fide_id

        self.knsb_id = knsb_id
        self.fide_id = fide_id

        if not fide_id and self.knsb:
            self.fide_id = self.knsb.fide_id

    @cached_property
    def knsb(self) -> KnsbPlayer | None:
        if self.knsb_id:
            query = select(KnsbPlayer).where(KnsbPlayer.knsb_id == self.knsb_id)
            return db.session.execute(query).scalar_one()

    @cached_property
    def fide(self) -> FidePlayer | None:
        if self.fide_id:
            query = select(FidePlayer).where(FidePlayer.fide_id == self.fide_id)
            return db.session.execute(query).scalar_one()
    
    @cache
    def get_knsb_rating(self, periode: RatingPeriode) -> KnsbRating | None:
        if self.knsb_id is None:
            return
        
        datum = periode.als_datum()
        query = select(KnsbRating).where(KnsbRating.knsb_id == self.knsb_id, KnsbRating.date == datum)
        return db.session.execute(query).scalar()

    @cache
    def get_fide_rating(self, periode: RatingPeriode) -> FideRating | None:
        if self.fide_id is None:
            return 
        
        datum = periode.als_datum()
        query = select(FideRating).where(FideRating.fide_id == self.fide_id, FideRating.date == datum)
        return db.session.execute(query).scalar()
    
    @cache
    def heeft_partij_gespeeld(self) -> bool:
        """Check of de speler in de afgelopen twee jaar een partij heeft
        gespeeld die meetelt voor KNSB-rating. Deze functie kunnen we nog niet implementeren.
        We gaan er nu van uit dat dat wel het geval is als de speler een knsb-id heeft."""
        return self.knsb_id is not None
