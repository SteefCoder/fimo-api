from typing import Annotated, Self

from functools import cache, cached_property, lru_cache

from pydantic import Field, model_validator, field_validator
from pydantic.dataclasses import dataclass
from sqlmodel import select
from sqlalchemy.exc import MultipleResultsFound

from app.models import FidePlayer, FideRating, KnsbPlayer, KnsbRating, SessionDep

from .periode import RatingPeriode
from .exceptions import PlayerNotFoundError, InternalError

_session: SessionDep = None  # type: ignore

def set_session(session: SessionDep) -> None:
    global _session
    _session = session


def verify_session() -> None:
    if _session is None:
        raise InternalError("De database session is niet gedefinieerd.")

# De Speler moet bruikbaar zijn als key in een dict,
# omdat we @cache en @cached_property gebruiken.
# Daarom eq=False
@dataclass(eq=False)
class Speler:
    """De verbinding tussen het rekenmodel en de database."""

    knsb_id: Annotated[int | None, Field(gt=0)] = None
    fide_id: Annotated[int | None, Field(gt=0)] = None

    @model_validator(mode='after')
    def check_knsb_en_fide(self) -> Self:
        if not (self.knsb_id or self.fide_id):
            raise ValueError("Of de KNSB ID of de FIDE ID moet gegeven zijn!")
        
        self._knsb = None
        self._fide = None

        # Check de gegeven knsb_id en fide_id in de database.
        # Als die niet bestaat, proberen we het in te vullen.
        # We checken ook of de fide_id en knsb_id bij dezelfde
        # speler horen als ze beiden gegeven zijn.
        if self.knsb_id and not self.fide_id:
            self._knsb = self._get_knsb()
            self.fide_id = self._knsb.fide_id

        elif self.fide_id and not self.knsb_id:
            self._fide = self._get_fide()
            # Een extra call, maar goed
            self._knsb = self._get_knsb_from_fide()
            if self._knsb:
                self.knsb_id = self._knsb.knsb_id

        else:
            self._knsb = self._get_knsb()
            self._fide = self._get_fide()
            if self._knsb.fide_id and self._knsb.fide_id != self._fide.fide_id:
                raise ValueError(f"De gegeven KNSB ID en FIDE ID ({self.knsb_id} en {self.fide_id}) "
                                 "behoren niet tot dezelfde speler!")

        return self

    @cache
    def _get_knsb(self) -> KnsbPlayer:
        verify_session()

        result = _session.get(KnsbPlayer, self.knsb_id)
        if result:
            return result
            
        raise PlayerNotFoundError(f"De opgegeven KNSB ID ({self.knsb_id}) "
                                    "was niet gevonden in de KNSB database.")
    
    def _get_knsb_from_fide(self) -> KnsbPlayer | None:
        verify_session()

        query = select(KnsbPlayer).where(KnsbPlayer.fide_id == self.fide_id)
        try:
            return _session.exec(query).one_or_none()
        except MultipleResultsFound:
            raise InternalError("Meerdere spelers gevonden met dezelfde FIDE ID.")
    
    @cache
    def _get_fide(self) -> FidePlayer:
        verify_session()

        result = _session.get(FidePlayer, self.fide_id)
        if result:
            return result
            
        raise PlayerNotFoundError(f"De opgegeven FIDE ID ({self.fide_id}) "
                                    "was niet gevonden in de FIDE database.")

    @cached_property
    def knsb(self) -> KnsbPlayer | None:
        if self.knsb_id:
            return self._get_knsb()
        
    @cached_property
    def fide(self) -> FidePlayer | None:
        if self.fide_id:
            return self._get_fide()
    
    @cache
    def get_knsb_rating(self, periode: RatingPeriode) -> KnsbRating | None:
        if self.knsb_id is None:
            return
        
        verify_session()
        datum = periode.als_datum()
        return _session.get(KnsbRating, (self.knsb_id, datum))
    
    @cache
    def get_fide_rating(self, periode: RatingPeriode) -> FideRating | None:
        if self.fide_id is None:
            return 
        
        verify_session()
        datum = periode.als_datum()
        return _session.get(FideRating, (self.fide_id, datum))

    @cache
    def heeft_partij_gespeeld(self) -> bool:
        """Check of de speler in de afgelopen twee jaar een partij heeft
        gespeeld die meetelt voor KNSB-rating. Deze functie kunnen we nog niet implementeren.
        We gaan er nu van uit dat dat wel het geval is als de speler een knsb-id heeft."""
        return self.knsb_id is not None
