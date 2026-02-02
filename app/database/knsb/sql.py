import datetime
import sqlite3

from download_list import load_full_rating_archive, load_knsb_rating
from ratingviewer_list import load_knsb_player


def refresh_knsb_player(con: sqlite3.Connection) -> None:
    """
    Refreshes and replaces the `knsb_player` table.
    Run once a month.
    """
    # TODO - also use the download list for optimal coverage.
    df = load_knsb_player()
    df.to_sql('knsb_player', con, if_exists='replace')


def fill_knsb_rating(con: sqlite3.Connection, start_date: datetime.date | None = None) -> None:
    """
    Fills the `knsb_rating` table.
    For staying up-to-date, use `update_knsb_rating`.

    It's a lot of lists to go through from the first record, so instead
    we can start from `start_date` and incrementally add lists when we feel like it. 
    """
    df = load_full_rating_archive(start_date)
    df.to_sql('knsb_rating', con, if_exists='append')


def update_knsb_rating(con: sqlite3.Connection) -> None:
    """
    Updates the `knsb_player` table. Adds to any existing table.
    Run once a month.
    """
    df = load_knsb_rating(datetime.date.today().replace(day=1))
    if df is None:
        return

    df.to_sql('knsb_rating', con, if_exists='append')
