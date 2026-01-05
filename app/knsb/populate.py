import io
import json
import os
import sqlite3
import zipfile

import dotenv
import pandas as pd
import requests

dotenv.load_dotenv()

# use defaults for the type checker
KEY = bytes(os.environ.get("DATA_KEY", ""), "utf8")
BASE_URL = os.environ.get("DATA_URL", "")
assert KEY != "" and BASE_URL != ""


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
        name = f"{p.achternaam}, {p.voornaam} ({p.voorletters})"
        if p.tussenvoegsels:
            return f"{p.tussenvoegsels} " + name
        else:
            return name
        
    return pd.DataFrame(dict(
        knsb_id=players.relatienummer,
        fide_id=players.fide_id.astype(pd.Int64Dtype()),
        name=[make_name(p) for _, p in players.iterrows()],
        title=metrics.title,
        fed=players.federation,
        birthyear=players.geboortejaar.astype(pd.Int64Dtype()),
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


def insert_knsb_player(conn: sqlite3.Connection):
    df = create_knsb_player()
    df.to_sql('knsb_player', conn, if_exists='replace')


def main():
    conn = sqlite3.connect('instance/database.db')
    insert_knsb_player(conn)


if __name__ == '__main__':
    main()