from . import bp

from app.models import FidePlayer, db

from sqlalchemy import select, Select


def execute(query: Select):
    return [x._tuple()[0].asdict() for x in db.session.execute(query).all()]


@bp.route('/players')
def players():
    query = select(FidePlayer).limit(10)
    return execute(query)
