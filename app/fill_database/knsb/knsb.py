import datetime
import sqlite3

from download_list import load_knsb_rating, load_full_rating_archive
from ratingviewer_list import load_knsb_player


def refresh_knsb_player(con: sqlite3.Connection) -> None:
    """
    Refreshes and replaces the `knsb_player` table.
    Run once a month.
    """
    # TODO - also use the download list for optimal coverage.
    df = load_knsb_player()
    df.to_sql('knsb_player', con, if_exists='replace')


def fill_knsb_rating(con: sqlite3.Connection) -> None:
    """
    Fills the `knsb_rating` table. Replaces any existing table.
    Run once, then use `update_knsb_rating` to keep up-to-date.
    """
    df = load_full_rating_archive()
    df.to_sql('knsb_rating', con, if_exists='replace')


def update_knsb_rating(con: sqlite3.Connection) -> None:
    """
    Updates the `knsb_player` table. Adds to any existing table.
    Run once a month.
    """
    df = load_knsb_rating(datetime.date.today().replace(day=1))
    if df is None:
        return

    df.to_sql('knsb_rating', con, if_exists='append')
