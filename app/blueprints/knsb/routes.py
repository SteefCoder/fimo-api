from dataclasses import asdict

from flask import request
from sqlalchemy import Select, select

from app.models import KnsbPlayer, KnsbRating, db
from app.rating import (Partij, PartijType, RatingContext, RatingPeriode,
                        Resultaat, Speler, bereken_nieuwe_rating)

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


@bp.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    speler_data = data['speler']
    speler = Speler(**speler_data)
    ctx = RatingContext(
        PartijType(data['partijtype']),
        RatingPeriode.uit_iso(data['datum'])
    )
    partijen = [
        Partij(
            speler,
            Speler(**partij_data['tegenstander']),
            Resultaat(partij_data['resultaat']),
            ctx
        )
        for partij_data in data['partijen']
    ]

    resultaat = bereken_nieuwe_rating(speler, ctx, partijen)
    return asdict(resultaat)
