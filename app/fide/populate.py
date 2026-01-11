import datetime
import sqlite3

import pandas as pd

MONTHS = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun',
          7: 'jul', 8: 'aug', 9: 'sep', 10: 'okt', 11: 'nov', 12: 'dec'}


def insert_fide_player_legacy(con: sqlite3.Connection):
    url = "http://ratings.fide.com/download/players_list_legacy.zip"
    with pd.read_fwf(url, compression='zip', chunksize=50_000, na_values=['', 0]) as reader:
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


def insert_temp_fide_rating(con, url: str, temp_table_name: str, date: datetime.date):
    widths = [15, 61, 4, 4, 5, 5, 15, 4, 6, 4, 3, 6, 5]

    rating_column = date.strftime("%b%y").upper()
    total_size = 0
    with pd.read_fwf(url, compression='zip', chunksize=10_000, widths=widths) as reader:
        for chunk in reader:
            chunk.rename(columns={"ID Number": "ID", rating_column: "Rating"}, inplace=True)
            chunk.drop_duplicates()
            chunk.set_index('ID', inplace=True)
            chunk["Date"] = date.isoformat()
            chunk.to_sql(temp_table_name, con, if_exists='append', method=None)
            total_size += len(chunk)

    print(f"Inserted records of {date.isoformat()} into {temp_table_name}! ({total_size} records)")


def insert_fide_rating(con: sqlite3.Connection):
    existing_records = con.execute("SELECT DISTINCT Date FROM fide_rating;").fetchall()
    existing_records = [x[0] for x in existing_records]
    print(existing_records)
    
    today = datetime.date.today()
    first_record = datetime.date(2015, 2, 1)
    for year in range(2026, 2015, -1):
        for month in range(12, 0, -1):
            date = datetime.date(year, month, 1)
            if date > today or date < first_record or date.isoformat() in existing_records:
                continue
            
            url = "https://ratings.fide.com/download/{}_" + date.strftime("%b%y").lower() + "frl.zip"
            insert_temp_fide_rating(con, url.format("standard"), "fide_standard", date)
            insert_temp_fide_rating(con, url.format("rapid"), "fide_rapid", date)
            insert_temp_fide_rating(con, url.format("blitz"), "fide_blitz", date)


def main():
    con = sqlite3.connect('instance/database.db')
    insert_fide_rating(con)


main()
