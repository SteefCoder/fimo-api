import datetime
import sqlite3

from dateutil.rrule import MONTHLY, rrule

from ..meta import (existing_ratings, remove_rating_meta, write_player_meta,
                    write_rating_meta)
from .download_list import download_ratings, read_legacy_format_players

import pandas as pd

def refresh_fide_player(con: sqlite3.Connection) -> None:
    """
    Refreshes and replaces the `fide_player` table.
    Run once a month.
    """
    #df = read_legacy_format_players()
    #df.to_sql('fide_player', con, if_exists='replace')
    df = pd.read_sql('select * from fide_player', con)
    # Add list information to meta file.
    write_player_meta(df, 'fide')


def delete_player_rating(con: sqlite3.Connection, date: datetime.date) -> int:
    count_query = "SELECT COUNT(*) FROM fide_rating WHERE date = ?;"
    delete_query = "DELETE FROM fide_rating WHERE date = ?;"

    count = con.execute(count_query, [date.isoformat()]).fetchone()[0]
    con.execute(delete_query, [date.isoformat()])
    con.commit()

    remove_rating_meta(date, 'fide')

    return count


def fill_fide_rating(
    con: sqlite3.Connection,
    start_date: datetime.date | None = None,
    force_refresh: bool = False
) -> None:
    """
    Fills the `fide_rating` table.
    For staying up-to-date, use `update_fide_rating`.

    It's a lot of lists to go through from the first record, so instead
    we can start from `start_date` and incrementally add lists when we feel like it. 
    """
    today = datetime.date.today()
    # First record available for download on the FIDE site.
    first_record = datetime.date(2015, 2, 1)

    start = start_date if start_date and start_date >= first_record else first_record
    skip_dates = existing_ratings('fide')

    # Iterate over every month from start to today
    dates = list(rrule(MONTHLY, dtstart=start, until=today))
    for period in reversed(dates):
        date = period.date()
        if start_date and date < start_date:
            continue

        if date in skip_dates:
            if not force_refresh:
                continue
            delete_player_rating(con, date)

        ratings = download_ratings(date)
        ratings.to_sql('fide_rating', con, if_exists='append')
        write_rating_meta(ratings, date, 'fide')


def update_fide_rating(con: sqlite3.Connection, force_refresh: bool = False) -> None:
    """
    Updates the `fide_player` table. Adds to any existing table.
    Run once a month.
    """
    today = datetime.date.today().replace(day=1)
    if today in existing_ratings('fide'):
        if not force_refresh:
            return
        delete_player_rating(con, today)

    ratings = download_ratings(today)
    ratings.to_sql('fide_rating', con, if_exists='append')
    write_rating_meta(ratings, today, 'fide')


def main():
    con = sqlite3.connect('instance/database.db')
    refresh_fide_player(con)
    update_fide_rating(con)


if __name__ == '__main__':
    main()