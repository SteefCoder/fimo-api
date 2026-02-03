from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from app.models import KnsbPlayer, KnsbRating, SessionDep
from app.rating import (BerekeningsResultaat, Partij, RatingContext, Speler,
                        bereken_nieuwe_rating, set_session)


class GameList(BaseModel):
    speler: Speler
    ctx: RatingContext
    partijen: list[Partij]

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


@router.post('/calculate', response_model=BerekeningsResultaat)
def calculate_rating(session: SessionDep, game_list: GameList):
    """
    Calculate the new rating of a player based on recent games played.
    """
    set_session(session)
    resultaat = bereken_nieuwe_rating(
        game_list.speler,
        game_list.ctx,
        game_list.partijen
    )
    return resultaat
