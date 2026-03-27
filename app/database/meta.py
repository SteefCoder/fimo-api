from __future__ import annotations

import datetime
import json
import pathlib
from contextlib import contextmanager
from dataclasses import dataclass

import pandas as pd

meta_file = pathlib.Path.cwd() / 'instance' / 'meta.json'


@dataclass(frozen=True, order=True)
class RatingPeriod:
    year: int
    month: int

    @classmethod
    def current(cls) -> RatingPeriod:
        today = datetime.date.today()
        return cls.from_date(today)
    
    @classmethod
    def from_date(cls, date: datetime.date) -> RatingPeriod:
        return cls(date.year, date.month)

    @classmethod
    def from_iso(cls, iso: str) -> RatingPeriod:
        return cls.from_date(datetime.date.fromisoformat(iso))
    
    def contains(self, date: datetime.date) -> bool:
        return date.replace(day=1) == self.as_date()

    def as_date(self) -> datetime.date:
        return datetime.date(self.year, self.month, 1)

    def isoformat(self) -> str:
        return self.as_date().isoformat()
    

@contextmanager
def open_meta(mode: str = 'r'):
    if meta_file.exists():
        with meta_file.open(encoding='utf8') as f:
            meta = json.load(f)
    else:
        meta = {}
    
    try:
        yield meta
    finally:
        if mode == 'w':
            with meta_file.open('w', encoding='utf8') as f:
                json.dump(meta, f, indent=2)


def today_iso() -> str:
    return datetime.date.today().isoformat()


def write_player_meta(df: pd.DataFrame, source: str) -> None:
    key = f'{source}-player'
    inactive = {'inactive': sum(~df['active'])} if source == 'fide' else {}
    with open_meta('w') as meta:
        meta[key] = {
            'records': len(df),
            'last-updated': today_iso(),
            'date': RatingPeriod.current().isoformat()
        } | inactive


def write_rating_meta(df: pd.DataFrame, period: RatingPeriod, source: str) -> None:
    key = f'{source}-rating'

    with open_meta('w') as meta:
        rating = meta.setdefault(key, {})
        rating.setdefault('lists', [])
        rating.setdefault('total-records', 0)

        inactive = {'inactive': sum(~df['active'])} if source == 'fide' else {}
        rating['lists'].append({
            'date': period.isoformat(),
            'updated-at': today_iso(),
            'records': len(df),
            'standard': sum(~df['standard_rating'].isna()),
            'rapid': sum(~df['rapid_rating'].isna()),
            'blitz': sum(~df['blitz_rating'].isna()),
        } | inactive)
        rating['total-records'] += len(df)
        rating['last-updated'] = today_iso()


def existing_ratings(source: str) -> list[RatingPeriod]:
    key = f'{source}-rating'

    with open_meta() as meta:
        rating = meta.get(key, {})
        if not 'lists' in rating:
            return []
        
        return [RatingPeriod.from_iso(x['date']) for x in rating['lists']]


def player_is_to_date(source: str) -> bool:
    key = f'{source}-player'

    with open_meta() as meta:
        player = meta.get(key, {})
        period = RatingPeriod.from_iso(player['date'])
        return period == RatingPeriod.current()
    

def remove_rating_meta(period: RatingPeriod, source: str) -> bool:
    key = f'{source}-rating'

    with open_meta('w') as meta:
        rating = meta.get(key, {})
        lists = rating.get('lists', [])

        for i, l in enumerate(lists):
            if l['date'] == period.isoformat():
                lists.pop(i)
                rating['total-records'] -= l['records']
                return True
            
        return False
