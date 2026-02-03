from fastapi import APIRouter
from sqlmodel import select

from app.models import FidePlayer, FideRating, SessionDep

router = APIRouter()


@router.get('/players', response_model=list[FidePlayer])
def read_players(session: SessionDep):
    query = select(FidePlayer).limit(10)
    return session.exec(query).all()


@router.get('/ratings', response_model=list[FideRating])
def ratings(session: SessionDep):
    query = select(FideRating).limit(10)
    return session.exec(query).all()
