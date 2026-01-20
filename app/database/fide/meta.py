from contextlib import contextmanager
import datetime
import json
import pathlib

import pandas as pd


meta_file = pathlib.Path.cwd() / 'instance' / 'meta.json'


def read_meta():
    with meta_file.open() as f:
        return json.load(f)


@contextmanager
def open_meta():
    with meta_file.open() as f:
        meta = json.load(f)
    
    try:
        yield meta
    finally:
        with meta_file.open('w', encoding='utf8') as f:
            json.dump(meta, f, indent=2)


def today_iso() -> str:
    return datetime.date.today().isoformat()


def write_player_meta(df: pd.DataFrame):
    unrated = (
        df['standard_rating'].isna() &
        df['rapid_rating'].isna() &
        df['blitz_rating'].isna()
    ).sum()

    with open_meta() as meta:
        meta['fide-player'] = {
            'records': len(df),
            'last-updated': today_iso(),
            'inactive': (~df['active']).sum(),
            'unrated': unrated
        }


def write_rating_meta(df: pd.DataFrame, date: datetime.date):
    with open_meta() as meta:
        meta['fide-rating']['lists'].append({
            'date': date,
            'records': len(df),
            'inactive': (~df['active']).sum(),
            'standard': (~df['standard'].isna()).sum(),
            'rapid': (~df['rapid'].isna()).sum(),
            'blitz': (~df['blitz'].isna()).sum(),
        })
        meta['fide-rating']['total-records'] += len(df)
        meta['fide-rating']['last-updated'] = today_iso()


def rating_exists_meta(date: datetime.date):
    meta = read_meta()
    return date.isoformat() in {x['date'] for x in meta['fide-rating']['lists']}
