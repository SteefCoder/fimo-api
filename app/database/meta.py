import datetime
import json
import pathlib
from contextlib import contextmanager

import pandas as pd

meta_file = pathlib.Path.cwd() / 'instance' / 'meta.json'


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
    unrated = sum(
        df['standard_rating'].isna() &
        df['rapid_rating'].isna() &
        df['blitz_rating'].isna()
    )

    key = f'{source}-player'
    inactive = {'inactive': (~df['active']).sum()} if source == 'fide' else {}
    with open_meta('w') as meta:
        meta[key] = {
            'records': len(df),
            'last-updated': today_iso(),
            'unrated': unrated
        } | inactive


def write_rating_meta(df: pd.DataFrame, date: datetime.date, source: str) -> None:
    key = f'{source}-rating'

    with open_meta('w') as meta:
        rating = meta.setdefault(key, {})
        rating.setdefault('lists', [])
        rating.setdefault('total-records', 0)

        inactive = {'inactive': sum(~df['active'])} if source == 'fide' else {}
        rating['lists'].append({
            'date': date.isoformat(),
            'updated-at': today_iso(),
            'records': len(df),
            'standard': sum(~df['standard_rating'].isna()),
            'rapid': sum(~df['rapid_rating'].isna()),
            'blitz': sum(~df['blitz_rating'].isna()),
        } | inactive)
        rating['total-records'] += len(df)
        rating['last-updated'] = today_iso()


def existing_ratings(source: str) -> list[datetime.date]:
    key = f'{source}-rating'

    with open_meta() as meta:
        rating = meta.get(key, {})
        if not 'lists' in rating:
            return []
        
        return [datetime.date.fromisoformat(x['date']) for x in rating['lists']]


def remove_rating_meta(date: datetime.date, source: str) -> bool:
    key = f'{source}-rating'

    with open_meta('w') as meta:
        rating = meta.get(key, {})
        lists = rating.get('lists', [])

        for i, l in enumerate(lists):
            if l['date'] == date.isoformat():
                lists.pop(i)
                rating['total-records'] -= l['records']
                return True
            
        return False
