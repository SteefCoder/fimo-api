import datetime
import sqlite3

from download_list import load_knsb_rating, load_full_rating_archive


def fill_knsb_rating(con: sqlite3.Connection) -> None:
    df = load_full_rating_archive()
    df.to_sql('knsb_rating', con, if_exists='replace')


def update_knsb_rating(con: sqlite3.Connection) -> None:
    df = load_knsb_rating(datetime.date.today().replace(day=1))
    if df is None:
        return

    df.to_sql('knsb_rating', con, if_exists='append')
