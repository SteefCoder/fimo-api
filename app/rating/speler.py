from functools import cache, cached_property

from pydantic import BaseModel

from app.models import FidePlayer, FideRating, KnsbPlayer, KnsbRating, SessionDep

from .periode import RatingPeriode
from .exceptions import PlayerNotFoundError

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
        if not self.knsb_id:
            return
        
        result = _session.get(KnsbPlayer, self.knsb_id)
        if result:
            return result
            
        raise PlayerNotFoundError(f"Player {self.knsb_id} was not found in KNSB database.")

    @cached_property
    def fide(self) -> FidePlayer | None:
        if self.fide_id:
            fide_id = self.fide_id
        elif self.knsb and self.knsb.fide_id:
            fide_id = self.knsb.fide_id
        else:
            return
        
        result = _session.get(FidePlayer, fide_id)
        if result:
            return result
        
        raise PlayerNotFoundError(f"Player {fide_id} was not found in FIDE database.")
        
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
