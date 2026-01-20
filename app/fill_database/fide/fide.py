import datetime
from dateutil.rrule import rrule, MONTHLY
import sqlite3

from download_list import read_legacy_format_players, download_ratings


def refresh_fide_player(con: sqlite3.Connection) -> None:
    """
    Refreshes and replaces the `fide_player` table.
    Run once a month.
    """
    df = read_legacy_format_players()
    df.to_sql('fide_player', con, if_exists='replace')


def fill_fide_rating(con: sqlite3.Connection, start_date: datetime.date | None = None) -> None:
    """
    Fills the `fide_rating` table. Replaces any existing table.
    Run once, then use `update_fide_rating` to keep up-to-date.
    """
    today = datetime.date.today()
    # First record available for download on the FIDE site.
    first_record = datetime.date(2015, 2, 1)

    start = start_date if start_date and start_date >= first_record else first_record

    dates = list(rrule(MONTHLY, dtstart=start, until=today))
    for period in reversed(dates):
        ratings = download_ratings(period.date())
        ratings.to_sql('fide_rating', con, if_exists='append')


def update_fide_rating(con: sqlite3.Connection) -> None:
    """
    Updates the `fide_player` table. Adds to any existing table.
    Run once a month.
    """
    today = datetime.date.today().replace(day=1)
    ratings = download_ratings(today)
    ratings.to_sql('fide_rating', con, if_exists='append')
