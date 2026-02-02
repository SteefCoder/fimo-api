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


def write_player_meta(df: pd.DataFrame) -> None:
    unrated = (
        df['standard_rating'].isna() &
        df['rapid_rating'].isna() &
        df['blitz_rating'].isna()
    ).sum()

    with open_meta('w') as meta:
        meta['knsb-player'] = {
            'records': len(df),
            'last-updated': today_iso(),
            'unrated': unrated
        }


def write_rating_meta(df: pd.DataFrame, date: datetime.date) -> None:
    with open_meta('w') as meta:
        if 'knsb-rating' not in meta:
            meta['knsb-rating'] = {}
        if 'lists' not in meta['knsb-rating']:
            meta['knsb-rating']['lists'] = []
        if 'total-records' not in meta['knsb-rating']:
            meta['knsb-rating']['total-records'] = 0

        meta['knsb-rating']['lists'].append({
            'date': date,
            'updated-at': today_iso(),
            'records': len(df),
            'standard': (~df['standard'].isna()).sum(),
            'rapid': (~df['rapid'].isna()).sum(),
            'blitz': (~df['blitz'].isna()).sum(),
        })
        meta['knsb-rating']['total-records'] += len(df)
        meta['knsb-rating']['last-updated'] = today_iso()


def existing_ratings() -> list[datetime.date]:
    with open_meta() as meta:
        if not 'knsb-rating' in meta or not 'lists' in meta['knsb-rating']:
            return []
        
        return [datetime.date.fromisoformat(x['date']) for x in meta['knsb-rating']['lists']]


def remove_rating_meta(date: datetime.date) -> bool:
    with open_meta('w') as meta:
        if not 'knsb-rating' in meta or not 'lists' in meta['knsb-rating']:
            return False
        
        for i, l in meta['knsb-rating']['lists']:
            if l['date'] == date.isoformat():
                meta['knsb-rating']['lists'].pop(i)
                return True
            
        return False
