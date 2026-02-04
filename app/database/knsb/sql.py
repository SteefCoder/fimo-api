import datetime
import sqlite3

from ..meta import (existing_ratings, remove_rating_meta, write_player_meta,
                    write_rating_meta)
from .download_list import get_download_urls, load_knsb_rating, load_knsb_player
# from .ratingviewer_list import load_knsb_player


def refresh_knsb_player(con: sqlite3.Connection) -> None:
    """
    Refreshes and replaces the `knsb_player` table.
    Run once a month.
    """
    # TODO - also use the download list for optimal coverage.

    date = datetime.date.today().replace(day=1)
    df = load_knsb_player(date)
    if df is None:
        raise Exception("Uhmm not found")
    
    df.to_sql('knsb_player', con, if_exists='replace')
    write_player_meta(df, 'knsb')


def delete_player_rating(con: sqlite3.Connection, date: datetime.date) -> int:
    count_query = "SELECT COUNT(*) FROM knsb_rating WHERE date = ?;"
    delete_query = "DELETE FROM knsb_rating WHERE date = ?;"

    count = con.execute(count_query, [date.isoformat()]).fetchone()[0]
    con.execute(delete_query, [date.isoformat()])
    con.commit()

    remove_rating_meta(date, 'knsb')

    return count


def fill_knsb_rating(
    con: sqlite3.Connection,
    start_date: datetime.date | None = None,
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

    for date, date_urls in urls.items():
        if start_date and date < start_date:
            continue

        if date in skip_dates:
            if force_refresh:
                delete_player_rating(con, date)
            else:
                continue

        df = load_knsb_rating(date, date_urls)
        if df is None:
            continue

        df.to_sql('knsb_rating', con, if_exists='append')
        write_rating_meta(df, date, 'knsb')


def update_knsb_rating(con: sqlite3.Connection) -> None:
    """
    Updates the `knsb_player` table. Adds to any existing table.
    Run once a month.
    """
    date = datetime.date.today().replace(day=1)
    df = load_knsb_rating(date)
    if df is None:
        return

    df.to_sql('knsb_rating', con, if_exists='append')

    write_rating_meta(df, date, 'knsb')


def main():
    con = sqlite3.connect("instance/database.db")
    fill_knsb_rating(con, datetime.date(2025, 1, 1))
    # refresh_knsb_player(con)
    

if __name__ == '__main__':
    main()
