from sqlalchemy import Select, select

from app.models import FidePlayer, FideRating, db

from . import bp


def execute(query: Select):
    return [x._tuple()[0].asdict() for x in db.session.execute(query).all()]


@bp.route('/players')
def players():
    query = select(FidePlayer).limit(10)
    return execute(query)


@bp.route('/ratings')
def ratings():
    query = select(FideRating).limit(10)
    return execute(query)
