import pathlib
import sqlite3

from ..meta import (RatingPeriod, existing_ratings, player_is_to_date,
                    remove_rating_meta, write_player_meta, write_rating_meta)
from .download_list import (get_download_urls, load_knsb_player,
                            load_knsb_rating)

query_path = pathlib.Path(__file__).resolve().parent / 'fide_id_query.sql'


def fill_player_fide_id(con: sqlite3.Connection) -> None:
    con.executescript(query_path.open().read())
    con.commit()


def refresh_knsb_player(con: sqlite3.Connection, force_refresh: bool = False) -> None:
    """
    Refreshes and replaces the `knsb_player` table.
    If the table is already up to date, it can be forced anyway using force_refresh.
    Run once a month.
    """
    if player_is_to_date('knsb') and not force_refresh:
        return

    df = load_knsb_player(RatingPeriod.current())
    if df is None:
        raise Exception("Uhmm not found")
    
    df.to_sql('knsb_player', con, if_exists='replace')
    fill_player_fide_id(con)
    write_player_meta(df, 'knsb')


def delete_player_rating(con: sqlite3.Connection, period: RatingPeriod) -> int:
    count_query = "SELECT COUNT(*) FROM knsb_rating WHERE date = ?;"
    delete_query = "DELETE FROM knsb_rating WHERE date = ?;"

    count = con.execute(count_query, [period.isoformat()]).fetchone()[0]
    con.execute(delete_query, [period.isoformat()])
    con.commit()

    remove_rating_meta(period, 'knsb')

    return count


def fill_knsb_rating(
    con: sqlite3.Connection,
    start_period: RatingPeriod | None = None,
    force_refresh: bool = False
) -> None:
    """
    Fills the `knsb_rating` table.
    For staying up-to-date, use `update_knsb_rating`.

    It's a lot of lists to go through from the first record, so instead
    we can start from `start_date` and incrementally add lists when we feel like it. 
    """

    urls = get_download_urls()
    skip_dates = existing_ratings('knsb')

    for period, date_urls in urls.items():
        if start_period and period < start_period:
            continue

        if period in skip_dates:
            if force_refresh:
                delete_player_rating(con, period)
            else:
                continue

        df = load_knsb_rating(period, date_urls)
        if df is None:
            continue

        df.to_sql('knsb_rating', con, if_exists='append')
        write_rating_meta(df, period, 'knsb')


def update_knsb_rating(con: sqlite3.Connection, force_refresh: bool = False) -> None:
    """
    Updates the `knsb_player` table. Adds to any existing table.
    Run once a month.
    """
    today = RatingPeriod.current()
    if today in existing_ratings('knsb'):
        if not force_refresh:
            return
        delete_player_rating(con, today)

    df = load_knsb_rating(today)
    if df is None:
        return

    df.to_sql('knsb_rating', con, if_exists='append')
    write_rating_meta(df, today, 'knsb')
