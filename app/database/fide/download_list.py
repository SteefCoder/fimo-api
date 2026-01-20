import datetime

import pandas as pd

Int = pd.Int64Dtype()


def read_legacy_format_players() -> pd.DataFrame:
    """
    Reads the most recent FIDE rating list in (apperently) legacy format.
    This means the standard, blitz and rapid ratings are combined,
    and non rated players are included.
    """
    # Apparently FIDE does downloads over http.
    url = "http://ratings.fide.com/download/players_list_legacy.zip"

    df = pd.read_fwf(url, compression='zip', na_values=['', 0])
    players = pd.DataFrame(dict(
        fide_id=df['ID Number'],
        name=df['Name'],
        fed=df['Fed'],
        sex=df['Sex'],
        title=df['Tit'],
        woman_title=df['WTit'],
        other_titles=df['OTit'],
        birthyear=df['B-day'].astype(Int),
        active=~df['Flag'].str.contains('i', regex=False, na=False)
    ))
    players.set_index('fide_id', inplace=True)
    return players


def read_rating_zip(url: str, date: datetime.date) -> pd.DataFrame:
    """
    Reads a FIDE rating list from fwf (fixed width format).
    """
    if date.day != 1:
        raise ValueError("Date must have day=1")

    # Since the file will be fwf (fixed width format) these are the widths it uses.
    # Pandas doesn't always recognize these properly.
    widths = [15, 61, 4, 4, 5, 5, 15, 4, 6, 4, 3, 6, 5]

    rating_column = date.strftime("%b%y").upper()

    df = pd.read_fwf(url, compression='zip', na_values=['', 0], widths=widths)
    ratings = pd.DataFrame(dict(
        fide_id=df['ID Number'],
        date=date.isoformat(),
        title=df['Tit'],
        woman_title=df['WTit'],
        other_titles=df['OTit'],
        rating=df[rating_column].astype(Int),
        games=df['Gms'].astype(Int),
        k=df['K'].astype(Int),
        active=~df['Flag'].str.contains('i', regex=False, na=False)
    ))
    ratings.set_index('fide_id', inplace=True)
    return ratings


def combine_ratings(standard: pd.DataFrame, rapid: pd.DataFrame, blitz: pd.DataFrame) -> pd.DataFrame:
    sdf = standard.rename(columns={'rating': 'standard_rating', 'games': 'standard_games', 'k': 'standard_k'})
    rdf = rapid.rename(columns={'rating': 'rapid_rating', 'games': 'rapid_games', 'k': 'rapid_k'})
    bdf = blitz.rename(columns={'rating': 'blitz_rating', 'games': 'blitz_games', 'k': 'blitz_k'})

    return sdf.combine_first(rdf).combine_first(bdf)


def download_ratings(date: datetime.date) -> pd.DataFrame:
    url = "http://ratings.fide.com/download/{}_" + date.strftime("%b%y").lower() + "frl.zip"

    standard_df = read_rating_zip(url.format("standard"), date)
    rapid_df = read_rating_zip(url.format("rapid"), date)
    blitz_df = read_rating_zip(url.format("blitz"), date)

    return combine_ratings(standard_df, rapid_df, blitz_df)
