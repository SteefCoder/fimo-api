from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import select

from app.models import KnsbPlayer, KnsbRating, SessionDep
from app.schemas import KnsbPlayerResponse, KnsbRatingResponse

from app.rating.db import DatabaseRepository
from app.rating.domain.exc import PlayerNotFoundError
from app.rating.verification import (LijstBerekening, PartijLijst,
                                     VerificationError, bereken_nieuwe_rating)

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


@router.get('/ratings', response_model=list[KnsbRatingResponse])
def read_ratings(session: SessionDep):
    """
    Get a list of rating records per date and player id.
    """
    query = select(KnsbRating).limit(10)
    return session.execute(query).scalars().all()


@router.post('/calculate', response_model=LijstBerekening)
def calculate_rating(session: SessionDep, lijst: PartijLijst):
    """
    Calculate the new rating of a player based on recent games played.
    """
    # TODO Unit tests voor het rating berekenen.
    # TODO Wat als de datum van de partij in de toekomst of ver verleden is?
    # TODO Als de datum heel ver in het verleden is (voordat er een rating record beschikbaar is)
    #  gebruiken we dan de lpr of geven we een error?
    try:
        repo = DatabaseRepository(session)
        resultaat = bereken_nieuwe_rating(lijst, repo)
    except (PlayerNotFoundError, VerificationError) as e:
        raise HTTPException(status_code=400, detail=e.args)

    return resultaat
