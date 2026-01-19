import sqlite3

from ratingviewer_list import load_knsb_player


def fill_knsb_player(con: sqlite3.Connection) -> None:
    # TODO - also use the download list for optimal coverage.
    df = load_knsb_player()
    df.to_sql('knsb_player', con, if_exists='replace')
