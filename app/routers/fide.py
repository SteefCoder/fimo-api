from fastapi import APIRouter
from sqlmodel import select

from app.models import FidePlayer, FideRating, SessionDep

router = APIRouter(prefix='/fide', tags=['fide'])


@router.get('/players', response_model=list[FidePlayer])
def read_players(session: SessionDep):
    """
    Get a list of players by name or id.
    """
    query = select(FidePlayer).limit(10)
    return session.exec(query).all()


@router.get('/ratings', response_model=list[FideRating])
def read_ratings(session: SessionDep):
    """
    Get a list of rating records per date and player id.
    """
    query = select(FideRating).limit(10)
    return session.exec(query).all()
