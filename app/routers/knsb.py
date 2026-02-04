from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import select

from app.models import KnsbPlayer, KnsbRating, SessionDep
from app.rating import (BerekeningsResultaat, Partij, RatingContext, Speler,
                        bereken_nieuwe_rating, set_session)
from app.rating.exceptions import RatingError, PlayerNotFoundError

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

    Wat dingen om over na te denken:
    - Als de datum heel ver in het verleden is (voordat er een rating record beschikbaar is)
      gebruiken we dan de lpr of geven we een error?
    - Wat doen we als de speler voor de knsb_id en de fide_id niet matchen?
      Waarschijnlijk negeren?
    - Hoe geven we aan waarom een partij niet meegeteld is?
      - De tegenstander bestaat niet (een error geven?)
      - De datum is in de toekomst of ver verleden
      - We kunnen een rating niet vinden
    - We willen het liefst de knsb en fide veel minder gretig opvragen uit de database
    - Wat doen we aan de herhaling van info in de request?
    - Hoe gaan we testen?
      - Om goed te testen moet de hele setup van de ratings anders.
    - Hoe doen we de verschillende formats (blitz, rapid en klassiek)?

    Wat willen we:
    input:
    speler
      - knsb_id
      - fide_id
    format (blitz, rapid of klassiek)
    partijen
      - tegenstander
        - knsb_id
        - fide_id
      - datum
      - resultaat

    output:
    nieuwe_rating
      - rating
      - nv_waarde (nieuwe nv_waarde)
      - bron
        - bron: berekend
        - huidige periode
    gespeelde_partijen (alleen de meegetelde)
    delta
    bonus
    lpr
    lpr-limitering
      - gelimiteerd: bool
      - bovengrens
      - ondergrens
    oude_rating
      - rating
      - nv_waarde
      - bron
        - bron (KS, FS, KB, LPR, etc.)
        - periode
          - maand
          - jaar
    partijen
    :als de partij meetelt:
      - partij telt mee: true
      - tegenstander
      - datum
      - resultaat
      - speler_rating (zelfde format als bovenstaand)
      - tegenstander_rating (zelfde als bovenstaand, zonder nv_waarde?)
      - W-We
      - k-waarde
      - delta
    :als de partij niet meetelt:
      - partij telt mee: false
      - tegenstander
      - datum
      - resultaat
      - reden
    """
    set_session(session)
    try:
        resultaat = bereken_nieuwe_rating(
            game_list.speler,
            game_list.ctx,
            game_list.partijen
        )
        return resultaat
    except (RatingError, PlayerNotFoundError) as e:
        raise HTTPException(400, e.args)
