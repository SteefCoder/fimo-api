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
def players(session: SessionDep):
    query = select(KnsbPlayer).limit(10)
    return session.exec(query).all()


@router.get('/ratings', response_model=list[KnsbRating])
def ratings(session: SessionDep):
    query = select(KnsbRating).limit(10)
    return session.exec(query).all()


@router.post('/calculate', response_model=BerekeningsResultaat)
def calculate(session: SessionDep, game_list: GameList):
    set_session(session)
    resultaat = bereken_nieuwe_rating(
        game_list.speler,
        game_list.ctx,
        game_list.partijen
    )
    return resultaat
