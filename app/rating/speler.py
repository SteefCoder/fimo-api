from functools import cache, cached_property

from pydantic import BaseModel

from app.models import FidePlayer, FideRating, KnsbPlayer, KnsbRating, SessionDep

from .periode import RatingPeriode


_session: SessionDep

def set_session(session: SessionDep) -> None:
    global _session
    _session = session


class Speler(BaseModel, frozen=True):
    """Een speler die vooral dingen doet die met databases te maken hebben."""

    knsb_id: int | None = None
    fide_id: int | None = None

    def model_post_init(self, __context):
        if not (self.knsb_id or self.fide_id):
            raise ValueError("Player must have some sort of id provided!")

    @cached_property
    def knsb(self) -> KnsbPlayer | None:
        if self.knsb_id:
            return _session.get(KnsbPlayer, self.knsb_id)

    @cached_property
    def fide(self) -> FidePlayer | None:
        if not self.fide_id and self.knsb and self.knsb.fide_id:
            return _session.get(FidePlayer, self.knsb.fide_id)

        if self.fide_id:
            return _session.get(FidePlayer, self.fide_id)

    @cache
    def get_knsb_rating(self, periode: RatingPeriode) -> KnsbRating | None:
        if self.knsb_id is None:
            return
        
        datum = periode.als_datum()
        return _session.get(KnsbRating, (self.knsb_id, datum))

    @cache
    def get_fide_rating(self, periode: RatingPeriode) -> FideRating | None:
        if self.fide_id is None:
            return 
        
        datum = periode.als_datum()
        return _session.get(FideRating, (self.fide_id, datum))

    @cache
    def heeft_partij_gespeeld(self) -> bool:
        """Check of de speler in de afgelopen twee jaar een partij heeft
        gespeeld die meetelt voor KNSB-rating. Deze functie kunnen we nog niet implementeren.
        We gaan er nu van uit dat dat wel het geval is als de speler een knsb-id heeft."""
        return self.knsb_id is not None
