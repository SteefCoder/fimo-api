from . import bp

from app.models import KnsbPlayer, db

from sqlalchemy import select


@bp.route('/players')
def players():
    query = select(KnsbPlayer).limit(10)
    return [x._tuple()[0].asdict() for x in db.session.execute(query).all()]
