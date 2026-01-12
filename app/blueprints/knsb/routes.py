from flask import request
from sqlalchemy import Select, select

from app.models import KnsbPlayer, KnsbRating, db
from app.rating import bereken_nieuwe_rating

from . import bp


def execute(query: Select):
    return [x.asdict() for x in db.session.execute(query).scalars()]


@bp.route('/players')
def players():
    query = select(KnsbPlayer).limit(10)
    return execute(query)


@bp.route('/ratings')
def ratings():
    query = select(KnsbRating).limit(10)
    return execute(query)
