from typing import Annotated

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.models import Depends, KnsbPlayer, KnsbRating, SessionDep, get_session
from app.rating.db import DatabaseRepository
from app.rating.domain.exc import PlayerNotFoundError
from app.rating.verification import (LijstBerekening, PartijLijst,
                                     VerificationError, bereken_nieuwe_rating)

router = APIRouter(prefix='/knsb', tags=['knsb'])


@router.get('/players', response_model=list[KnsbPlayer])
def read_players(session: SessionDep):
    """
    Get a list of players by name or id.
    """
    query = select(KnsbPlayer).limit(10)
    return session.exec(query).all()


@router.get('/ratings', response_model=list[KnsbRating])
def read_ratings(session: SessionDep):
    """
    Get a list of rating records per date and player id.
    """
    query = select(KnsbRating).limit(10)
    return session.exec(query).all()


@router.post(
    '/calculate',
    response_model=LijstBerekening,
    dependencies=[Depends(get_session)]
)
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
