from app.models import KnsbPlayer, FidePlayer, KnsbRating, FideRating, SessionDep
from .domain.exceptions import PlayerNotFoundError
from sqlmodel import select
from .periode import RatingPeriode


class DatabaseRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session
        
    def get_knsb(self, knsb_id: int) -> KnsbPlayer:
        result = self.session.get(KnsbPlayer, knsb_id)
        if result:
            return result
            
        raise PlayerNotFoundError(f"De opgegeven KNSB ID ({knsb_id}) "
                                    "was niet gevonden in de KNSB database.")
    
    def get_fide(self, fide_id: int) -> FidePlayer:
        result = self.session.get(FidePlayer, fide_id)
        if result:
            return result
            
        raise PlayerNotFoundError(f"De opgegeven FIDE ID ({fide_id}) "
                                    "was niet gevonden in de FIDE database.")
    
    def get_knsb_from_fide(self, fide_id: int) -> KnsbPlayer | None:
        query = select(KnsbPlayer).where(KnsbPlayer.fide_id == fide_id)
        return self.session.exec(query).one_or_none()

    def get_knsb_rating(self, knsb_id: int, periode: RatingPeriode) -> KnsbRating | None:
        return self.session.get(KnsbRating, (knsb_id, periode.als_datum()))

    def get_fide_rating(self, fide_id: int, periode: RatingPeriode) -> FideRating | None:
        return self.session.get(FideRating, (fide_id, periode.als_datum()))

    def heeft_partij_gespeeld(self, knsb_id: int) -> bool:
        return True
