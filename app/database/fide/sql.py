import sqlite3

from dateutil.rrule import MONTHLY, rrule

from ..meta import (existing_ratings, remove_rating_meta, write_player_meta,
                    write_rating_meta, RatingPeriod, player_is_to_date)
from .download_list import download_ratings, read_legacy_format_players


def refresh_fide_player(con: sqlite3.Connection, force_refresh: bool = False) -> None:
    """
    Refreshes and replaces the `fide_player` table.
    Run once a month.
    """
    if player_is_to_date('fide') and not force_refresh:
        return

    df = read_legacy_format_players()
    df.to_sql('fide_player', con, if_exists='replace')
    # Add list information to meta file.
    write_player_meta(df, 'fide')


def delete_player_rating(con: sqlite3.Connection, period: RatingPeriod) -> int:
    count_query = "SELECT COUNT(*) FROM fide_rating WHERE date = ?;"
    delete_query = "DELETE FROM fide_rating WHERE date = ?;"

    count = con.execute(count_query, [period.isoformat()]).fetchone()[0]
    con.execute(delete_query, [period.isoformat()])
    con.commit()

    remove_rating_meta(period, 'fide')

    return count


def fill_fide_rating(
    con: sqlite3.Connection,
    start_period: RatingPeriod | None = None,
    force_refresh: bool = False
) -> None:
    """
    Fills the `fide_rating` table.
    For staying up-to-date, use `update_fide_rating`.

    It's a lot of lists to go through from the first record, so instead
    we can start from `start_date` and incrementally add lists when we feel like it. 
    """

    current_period = RatingPeriod.current()
    # First record available for download on the FIDE site.
    first_record = RatingPeriod(2015, 2)

    start = start_period if start_period and start_period >= first_record else first_record
    skip_dates = existing_ratings('fide')

    # Iterate over every month from start to today
    dates = list(rrule(MONTHLY, dtstart=start.as_date(), until=current_period.as_date()))
    for period_date in reversed(dates):
        period = RatingPeriod.from_date(period_date.date())
        if start_period and period < start_period:
            continue

        if period in skip_dates:
            if not force_refresh:
                continue
            delete_player_rating(con, period)

        print(f"Starting download for {period}.")
        ratings = download_ratings(period)
        print("Download finished. Inserting to database.")
        ratings.to_sql('fide_rating', con, if_exists='append')
        write_rating_meta(ratings, period, 'fide')
        print("Done")


def update_fide_rating(con: sqlite3.Connection, force_refresh: bool = False) -> None:
    """
    Updates the `fide_player` table. Adds to any existing table.
    Run once a month.
    """
    current_period = RatingPeriod.current()
    if current_period in existing_ratings('fide'):
        if not force_refresh:
            return
        delete_player_rating(con, current_period)

    ratings = download_ratings(current_period)
    ratings.to_sql('fide_rating', con, if_exists='append')
    write_rating_meta(ratings, current_period, 'fide')
