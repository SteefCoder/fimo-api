"""
Program for automatically downloading the player lists the ratingviewer site uses.

These lists are mostly used internally, so I'd most like to just keep to the (public) download lists.
These contains the FIDE ID and register date of the players, which the download lists don't.

I'll be retiring this one.
"""

import datetime
import io
import json
import os
import zipfile

import dotenv
import pandas as pd
import requests

dotenv.load_dotenv()

Int = pd.Int64Dtype()

# Use defaults for the type checker.
DATA_KEY = bytes(os.environ.get('DATA_KEY', ""), 'utf8')
BASE_URL = os.environ.get('DATA_URL', "")
INDEX_URL = os.environ.get('INDEX_URL', "")
assert all((DATA_KEY != "", BASE_URL != "", INDEX_URL != ""))


def download_lists(url: str) -> dict[str, pd.DataFrame]:
    """
    Downloads the lists found at `url` to a DataFrame.
    The (encrypted) zip file from `url` usually contains `memberships.json` and `list_metrics.json`.
    """
    response = requests.get(url)
    response.raise_for_status()
    data_bytes = io.BytesIO(response.content)

    zf = zipfile.ZipFile(data_bytes)
    zf.setpassword(DATA_KEY)

    dfs = {}
    for file in zf.filelist:
        dfs[file.filename] = pd.DataFrame(json.load(zf.open(file)))
    return dfs


def create_player_list(players: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Creates the player list based on the players and metrics.
    The metrics are just needed for the title (since a title is something that could
    technically change per month).
    """
    # Build a full name in the format '[tussenvoegsels] achternaam, voornaam'.
    # The tussenvoegsels are not capitalized, so this action can be reversed.
    full_name = (
        players['tussenvoegsels']
        .fillna('')
        .str.cat(
            players['achternaam'].str.cat(players['voornaam'], sep=', ')
        )
        .str.strip()
    )

    df = pd.DataFrame(dict(
        knsb_id=players['relatienummer'],
        fide_id=players['fide_id'].astype(Int),
        name=full_name,
        title=metrics['title'],
        fed=players['federation'],
        birthyear=players['geboortejaar'].astype(Int),
        sex=players['geslacht'],
        register_date=players['begindatum']
    ))
    df.set_index('knsb_id')
    return df


def get_list_identifiers() -> list[tuple[datetime.date, str, str]]:
    """
    Gets the latest identifiers associated with a list.
    For example, the standard rating list of january 2026 has `list_id` 166.
    This together with the timestamp of the latest version of the list makes the identifier
    (eg 166-1768808718).

    The returned tuples contain the date (with day=1), the rating type (C, R, or B) and the identifier.
    """
    response = requests.get(INDEX_URL)
    response.raise_for_status()
    index = json.loads(response.content)

    items = []
    for item in index['items']:
        timestamp = datetime.datetime.fromisoformat(item['last_version']).timestamp()
        date = datetime.date(item['year'], item['month'], 1)
        items.append((date, item['category'], f"{item['list_id']}-{timestamp}"))
    return items


def load_knsb_player() -> pd.DataFrame:
    """
    Creates a DataFrame for the KnsbPlayer model.
    Uses the most recent two (standard) lists to prevent missing players.
    """
    lists = get_list_identifiers()
    # Filter by standard ('C') and sort by most recent, then take first two.
    identifiers = sorted(filter(lambda x: x[1] == 'C', lists), key=lambda x: x[0], reverse=True)[:2]

    dfs: list[pd.DataFrame] = []
    for l in identifiers:
        # Urls generally looks like {BASE_URL}/{identifier}.pdf
        # Don't ask me why it's .pdf (Epstein themed files ahh)
        url = BASE_URL + "/" + l[2] + ".pdf"
        list_dfs = download_lists(url)
        players, metrics = list_dfs['memberships.json'], list_dfs['list_metrics.json']
        dfs.append(create_player_list(players, metrics))
    
    df = pd.concat(dfs)
    # keep='first', since most recent DataFrame is added first.
    return df.loc[~df.index.duplicated(keep='first')]
