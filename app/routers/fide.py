from typing import Annotated

from fastapi import APIRouter, Query, Path, HTTPException, Depends
from sqlmodel import select

from app.rating.periode import RatingPeriode
from app.models import FidePlayer, FideRating, SessionDep
from app.schemas import FidePlayerResponse, FideRatingResponse

router = APIRouter(prefix='/fide', tags=['fide'])


@router.get('/players/search', response_model=list[FidePlayerResponse])
def search_players(
    session: SessionDep,
    name: Annotated[str, Query(max_length=50)],
    limit: Annotated[int, Query(gt=0, lt=100)] = 10,
):
    """
    Get a list of players by name or id.
    """
    query = select(FidePlayer).where(FidePlayer.name.contains(name, autoescape=True)).limit(limit)
    return session.execute(query).scalars()


@router.get('/players/{fide_id}', response_model=FidePlayerResponse)
def get_player(session: SessionDep, fide_id: Annotated[int, Path(gt=0)]):
    player = session.get(FidePlayer, fide_id)
    if player:
        return player
    
    raise HTTPException(404, f"Geen spelers gevonden met FIDE ID {fide_id}.")


@router.get('/ratings', response_model=list[FideRatingResponse])
def get_ratings(
    session: SessionDep,
    fide_id: Annotated[int, Query(gt=0)],
    date: Annotated[RatingPeriode, Depends(RatingPeriode.uit_datum)]
):
    """
    Get a list of rating records per date and player id.
    """
    rating = session.get(FideRating, (fide_id, date.als_datum()))
    if rating:
        return rating
    
    raise HTTPException(404, f"Geen rating gevonden")

