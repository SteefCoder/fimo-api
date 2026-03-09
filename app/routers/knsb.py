from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select

from app.models import KnsbPlayer, KnsbRating, SessionDep
from app.rating import (DatabaseRepository, GameList, ListCalculation,
                        PlayerNotFoundError, RatingPeriod, VerificationError,
                        calculate_new_rating)
from app.schemas import KnsbPlayerResponse, KnsbRatingResponse

router = APIRouter(prefix='/knsb', tags=['knsb'])


@router.get('/players/search', response_model=list[KnsbPlayerResponse])
def search_players(
    session: SessionDep,
    name: Annotated[str, Query(max_length=50)],
    limit: Annotated[int, Query(gt=0, lt=100)] = 10,
):
    """
    Get a list of players by name.
    """ 
    
    query = select(KnsbPlayer).where(KnsbPlayer.name.contains(name, autoescape=True)).limit(limit)
    return session.execute(query).scalars()


@router.get('/players/{knsb_id}', response_model=KnsbPlayerResponse)
def get_player(session: SessionDep, knsb_id: Annotated[int, Path(gt=0)]):
    player = session.get(KnsbPlayer, knsb_id)
    if player:
        return player
    
    raise HTTPException(404, f"Geen spelers gevonden met KNSB ID {knsb_id}.")


@router.get('/ratings', response_model=KnsbRatingResponse)
def get_ratings(
    session: SessionDep,
    knsb_id: Annotated[int, Query(gt=0)],
    date: Annotated[RatingPeriod, Depends(RatingPeriod.from_date)]
):
    """
    Get a list of rating records per date and player id.
    """
    rating = session.get(KnsbRating, (knsb_id, date.as_date()))
    if rating:
        return rating
    
    raise HTTPException(404, f"Geen rating gevonden")


@router.post('/calculate', response_model=ListCalculation)
def calculate_rating(session: SessionDep, game_list: GameList):
    """
    Calculate the new rating of a player based on recent games played.
    """
    # TODO Unit tests voor het rating berekenen.
    # TODO Wat als de datum van de partij in het ver verleden is?
    # TODO Als de berekendatum heel ver in het verleden is (voordat er een rating record beschikbaar is)
    #  gebruiken we dan de lpr of geven we een error?
    try:
        repo = DatabaseRepository(session)
        resultaat = calculate_new_rating(game_list, repo)
    except (PlayerNotFoundError, VerificationError) as e:
        raise HTTPException(status_code=400, detail=e.args)

    return resultaat
