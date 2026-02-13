"""
Program for automatically downloading the rating lists found on
https://schaakbond.nl/rating/downloadlijsten/

A downloaded list has approx 18k rows. See KnsbRating in app/models for info on the columns.
Note that the junior ratings are legacy and have been removed after september 2024.
Instead, the rapid and blitz ratings were introduced.
"""

import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

Int = pd.Int64Dtype()

MONTHS = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
          'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}


def get_download_urls() -> dict[datetime.date, dict[str, str]]:
    """Scrapes the urls for the download lists from the schaakbond website.
    I would like to just infer the urls from the date, since they mostly look like
    https://schaakbond.nl/wp-content/uploads/{year}/{month}/{year}-{month}-{rating_type}.zip
    
    But there are irregular exceptions where the month in either the filename or path
    is off by 1. I can't predict when this is, so I just scrape all urls.

    Returns a dict with key: value pairs like
    `date(year, month, 1): {rating_type1: url1, rating_type2: url2}`

    The possible rating types are `JEUGD` and `KNSB` for old lists (up to september 2024).
    For new lists, it's `KLASSIEK`, `RAPID`, and `SNEL`.
    """
    url = "https://schaakbond.nl/rating/downloadlijsten/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    archive_list = soup.find('div', attrs={'class': 'avia_textblock'}).find_all('ul')[1]  # type: ignore
    list_items = archive_list.find_all('li')

    base_urls = {}
    for item in list_items:
        href = item.find('a').attrs['href']  # type: ignore
        game_type = href.split('-')[-1][:-4]  # type: ignore

        text_list = item.text.strip().split()
        year = int(text_list[-1])
        month = MONTHS[text_list[-2]]
        
        date = datetime.date(year, month, 1)
        if date in base_urls:
            base_urls[date][game_type] = href
        else:
            base_urls[date] = {game_type: href}

    return base_urls


def read_rating_zip(url: str) -> pd.DataFrame:
    """Reads a rating list for a specific date and rating type. Fragile, don't touch.
    """
    names = ['knsb_id', 'name', 'title', 'fed', 'rating', 'games', 'birthyear', 'sex']
    
    return pd.read_csv(url, skiprows=1, encoding='latin1', sep=';', index_col='knsb_id',
                       names=names, dtype={'rating': Int, 'games': Int, 'birthyear': Int},
                       na_values=["#N/B", ""]).replace({'sex': {'w': 'V', pd.NA: 'M'}})


def combine_rating_old(rating_lists: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combines the `KNSB` and `JEUGD` rating lists (legacy format).
    All personal information is left out, since that can be found in the player database.
    """
    senior_df = rating_lists['KNSB']
    junior_df = rating_lists['JEUGD'].rename(columns={'rating': 'jrating', 'games': 'jgames'})

    # The junior df is smaller, so concat first to align the axes.
    df = pd.concat([senior_df, junior_df], axis=1)

    # Old KNSB rating is equivalent to the new standard rating.
    # Rapid and blitz don't exist yet, so those are all NULL.
    return pd.DataFrame(dict(
        title=df['title'],
        standard_rating=df['rating'],
        standard_games=df['games'],
        rapid_rating=pd.Series(pd.NA, dtype=Int),
        rapid_games=pd.Series(pd.NA, dtype=Int),
        blitz_rating=pd.Series(pd.NA, dtype=Int),
        blitz_games=pd.Series(pd.NA, dtype=Int),
        junior_rating=df['jrating'],
        junior_games=df['jgames']
    ), index=df.index)


def combine_rating_new(rating_lists: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combines the `KLASSIEK` and `RAPID`, and `SNEL` rating lists (standard, rapid, and blitz respectively).
    All personal information is left out, since that can be found in the player database.
    """
    standard_df = rating_lists['KLASSIEK']
    blitz_df = rating_lists['SNEL']
    rapid_df = rating_lists['RAPID']

    # For the newer lists, there is no junior rating anymore,
    # so those are all NULL.
    return pd.DataFrame(dict(
        title=standard_df['title'],
        standard_rating=standard_df['rating'],
        standard_games=standard_df['games'],
        rapid_rating=rapid_df['rating'],
        rapid_games=rapid_df['games'],
        blitz_rating=blitz_df['rating'],
        blitz_games=blitz_df['games'],
        junior_rating=pd.Series(pd.NA, dtype=Int),
        junior_games=pd.Series(pd.NA, dtype=Int)
    ), index=standard_df.index)


def combine_rating(rating_lists: dict[str, pd.DataFrame], date: datetime.date) -> pd.DataFrame:
    """
    Combines the different rating lists to one list with all ratings.
    All personal information is left out, since that can be found in the player database.
    Only the knsb_id is left for identification (the index column in the returned DataFrame). 
    """
    if date <= datetime.date(2024, 9, 1):
        df = combine_rating_old(rating_lists)
    else:
        df = combine_rating_new(rating_lists)

    df["date"] = date
    return df


def load_knsb_rating(date: datetime.date, date_urls: dict[str, str] | None = None) -> pd.DataFrame | None:
    """
    Loads the full rating list for a specific date. Note that this involves getting (scraping)
    the entire list of download urls. For loading all ratings lists, see `load_full_rating_archive`.
    """
    if date.day != 1:
        raise ValueError("Date must have day=1")

    if not date_urls:
        urls = get_download_urls()
        date_urls = urls.get(date, None)
        if date_urls is None:
            return
    
    rating_lists = {rating_type: read_rating_zip(url) for rating_type, url in date_urls.items()}
    return combine_rating(rating_lists, date)


def load_knsb_player(date: datetime.date) -> pd.DataFrame | None:
    if date.day != 1:
        raise ValueError("Date must have day=1")

    urls = get_download_urls()
    date_urls = urls.get(date, None)
    if date_urls is None:
        return
        
    df = read_rating_zip(date_urls["KLASSIEK"])[
        ['name', 'title', 'fed', 'birthyear', 'sex']
    ]
    df['fide_id'] = pd.Series(pd.NA, dtype=Int)
    return df
