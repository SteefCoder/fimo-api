from typing import Annotated

from fastapi import APIRouter, Path, Query
from sqlalchemy import select

from app.models import SessionDep, SuggestPlayer
from app.schemas import SuggestPlayerResponse

router = APIRouter(prefix='/suggest', tags=['suggest'])


@router.get('/', response_model=list[SuggestPlayerResponse])
def suggest(session: SessionDep, name: Annotated[str, Query(max_length=50)]):
    query = select(SuggestPlayer).where(
        SuggestPlayer.full_name.like(f"{name}%") |
        SuggestPlayer.comma_name.like(f"{name}%")
    ).limit(10)
    return session.execute(query).scalars()


@router.get('/knsb/{knsb_id}', response_model=SuggestPlayerResponse)
def suggest_knsb(session: SessionDep, knsb_id: Annotated[int, Path(gt=0)]):
    query = select(SuggestPlayer).where(SuggestPlayer.knsb_id == knsb_id)
    return session.execute(query).scalar_one_or_none()


@router.get('/fide/{fide_id}', response_model=SuggestPlayerResponse)
def suggest_fide(session: SessionDep, fide_id: Annotated[int, Path(gt=0)]):
    query = select(SuggestPlayer).where(SuggestPlayer.fide_id == fide_id)
    return session.execute(query).scalar_one_or_none()
