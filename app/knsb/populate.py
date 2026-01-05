import datetime
import io
import json
import os
import sqlite3
import zipfile

from bs4 import BeautifulSoup
import dotenv
import pandas as pd
import requests

dotenv.load_dotenv()

Int = pd.Int64Dtype()

# use defaults for the type checker
KEY = bytes(os.environ.get("DATA_KEY", ""), "utf8")
BASE_URL = os.environ.get("DATA_URL", "")
assert KEY != "" and BASE_URL != ""

MONTHS = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
          'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}


def get_knsb_rating_urls() -> dict[datetime.date, dict[str, str]]:
    url = "https://schaakbond.nl/rating/downloadlijsten/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    archive_list = soup.find("div", attrs={"class": "avia_textblock"}).find_all("ul")[1]  # type: ignore
    list_items = archive_list.find_all("li")

    base_urls = {}
    for item in list_items:
        href = item.find("a").attrs["href"]  # type: ignore
        game_type = href.split("-")[-1][:-4]  # type: ignore

        text_list = item.text.strip().split()
        year = int(text_list[-1])
        month = MONTHS[text_list[-2]]
        
        date = datetime.date(year, month, 1)
        if date in base_urls:
            base_urls[date][game_type] = href
        else:
            base_urls[date] = {game_type: href}

    return base_urls


def read_knsb_rating_zip(url: str) -> pd.DataFrame:
    names = ['knsb_id', 'name', 'title', 'fed', 'rating', 'games', 'birthyear', 'sex']
    
    return pd.read_csv(url, skiprows=1, encoding='latin1', sep=';', index_col='knsb_id',
                       names=names, dtype={'rating': Int, 'games': Int, 'birthyear': Int},
                       na_values=["#N/B", ""]).replace({'sex': {'w': 'V', pd.NA: 'M'}})


def combine_knsb_rating_old(urls: dict[str, str]) -> pd.DataFrame:
    senior_df = read_knsb_rating_zip(urls["KNSB"])
    junior_df = read_knsb_rating_zip(urls["JEUGD"]).rename(columns={'rating': 'jrating', 'games': 'jgames'})

    # the junior df is smaller, so concat first to align the axes
    df = pd.concat([senior_df, junior_df], axis=1)

    # Old KNSB rating is equivalent to the new standard rating
    return pd.DataFrame(dict(
        standard_rating=df.rating,
        standard_games=df.games,
        rapid_rating=pd.Series(pd.NA, dtype=Int),
        rapid_games=pd.Series(pd.NA, dtype=Int),
        blitz_rating=pd.Series(pd.NA, dtype=Int),
        blitz_games=pd.Series(pd.NA, dtype=Int),
        junior_rating=df.jrating,
        junior_games=df.jgames
    ), index=df.index).drop_duplicates()


def combine_knsb_rating_new(urls: dict[str, str]) -> pd.DataFrame:
    standard_df = read_knsb_rating_zip(urls["KLASSIEK"])
    blitz_df = read_knsb_rating_zip(urls["SNEL"])
    rapid_df = read_knsb_rating_zip(urls["RAPID"])

    return pd.DataFrame(dict(
        standard_rating=standard_df.rating,
        standard_games=standard_df.games,
        rapid_rating=rapid_df.rating,
        rapid_games=rapid_df.games,
        blitz_rating=blitz_df.rating,
        blitz_games=blitz_df.games,
        junior_rating=pd.Series(pd.NA, dtype=Int),
        junior_games=pd.Series(pd.NA, dtype=Int)
    ), index=standard_df.index).drop_duplicates()


def combine_knsb_rating(urls: dict[str, str], date: datetime.date) -> pd.DataFrame:
    if date <= datetime.date(2024, 9, 1):
        df = combine_knsb_rating_old(urls)
    else:
        df = combine_knsb_rating_new(urls)
    df["date"] = date
    return df


def load_knsb_rating(date: datetime.date) -> pd.DataFrame | None:
    assert date.day == 1

    urls = get_knsb_rating_urls()
    date_urls = urls.get(date, None)
    if date_urls is None:
        return
    
    return combine_knsb_rating(date_urls, date)


def load_knsb_rating_archive() -> pd.DataFrame:
    urls = get_knsb_rating_urls()

    dfs = []
    for date, date_urls in urls.items():
        df = combine_knsb_rating(date_urls, date)
        dfs.append(df)

    return pd.concat(dfs)


def get_list(url: str) -> dict[str, pd.DataFrame]:
    response = requests.get(url)
    response.raise_for_status()
    data_bytes = io.BytesIO(response.content)

    zf = zipfile.ZipFile(data_bytes)
    zf.setpassword(KEY)

    dfs = {}
    for file in zf.filelist:
        dfs[file.filename] = pd.DataFrame(json.load(zf.open(file)))
    return dfs


def build_list(players: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    def make_name(p):
        name = f"{p.achternaam}, {p.voornaam}"
        if p.tussenvoegsels:
            return f"{p.tussenvoegsels} " + name
        else:
            return name
        
    return pd.DataFrame(dict(
        knsb_id=players.relatienummer,
        fide_id=players.fide_id.astype(Int),
        name=[make_name(p) for _, p in players.iterrows()],
        title=metrics.title,
        fed=players.federation,
        birthyear=players.geboortejaar.astype(Int),
        sex=players.geslacht,
        start_date=players.begindatum
    ))


def create_knsb_player():
    # TODO -- get these (the latest two or smth) automatically
    lists = ["166-1767599049", "163-1767599027"]

    dfs: list[pd.DataFrame] = []
    for l in lists:
        url = BASE_URL + "/" + l + ".pdf"
        list_dfs = get_list(url)
        players, metrics = list_dfs['memberships.json'], list_dfs['list_metrics.json']
        dfs.append(build_list(players, metrics))
    
    return pd.concat(dfs).drop_duplicates('knsb_id', inplace=False).set_index('knsb_id')


def insert_knsb_rating(con: sqlite3.Connection):
    # load the entire archive, do this only once
    df = load_knsb_rating_archive()
    df.to_sql('knsb_rating', con, if_exists='replace')

    # when updating, just use this
    #date = datetime.date.today().replace(day=1)
    #df = load_knsb_rating(date)
    #if df is None:
    #    return
    #df.to_sql('knsb_rating', con, if_exists='append')


def insert_knsb_player(con: sqlite3.Connection):
    df = create_knsb_player()
    df.to_sql('knsb_player', con, if_exists='replace')


def main():
    con = sqlite3.connect('instance/database.db')
    insert_knsb_rating(con)


if __name__ == '__main__':
    main()