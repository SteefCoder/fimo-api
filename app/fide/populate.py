import sqlite3

import pandas as pd


def insert_fide_player_legacy(con: sqlite3.Connection):
    url = "http://ratings.fide.com/download/players_list_legacy.zip"
    with pd.read_fwf(url, compression='zip', chunksize=50_000, na_values=['', 0]) as reader:
        chunks = 0
        for chunk in reader:
            df = pd.DataFrame(dict(
                fide_id=chunk['ID Number'],
                name=chunk['Name'],
                fed=chunk.Fed,
                sex=chunk.Sex,
                title=chunk.Tit,
                woman_title=chunk.WTit,
                other_titles=chunk.OTit,
                birthyear=chunk['B-day'].astype(pd.Int64Dtype()),
                active=~chunk.Flag.str.contains('i', regex=False, na=False)
            ))
            df.drop_duplicates()
            df.set_index('fide_id', inplace=True)
            df.to_sql('fide_player', con, if_exists='append')
            chunks += 1
            print(f"Chunk {chunks} done")


def main():
    con = sqlite3.connect('instance/database.db')
    insert_fide_player_legacy(con)


main()