import argparse
import sqlite3

from app.database.fide.sql import (fill_fide_rating, refresh_fide_player,
                                   update_fide_rating)
from app.database.knsb.sql import (fill_knsb_rating, refresh_knsb_player,
                                   update_knsb_rating)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fed', choices=['knsb', 'fide', 'all'], default='all')
    parser.add_argument('--table', choices=['rating', 'player', 'all'], default='all')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    con = sqlite3.connect('instance/database.db')

    if args.fed in ('all', 'fide'):
        if args.table in ('all', 'rating'):
            print("Updating fide rating...")
            update_fide_rating(con, args.force)
        if args.table in ('all', 'player'):
            print("Updating fide player...")
            refresh_fide_player(con, args.force)

    if args.fed in ('all', 'knsb'):
        if args.table in ('all', 'rating'):
            print("Updating knsb rating...")
            update_knsb_rating(con, args.force)
        if args.table in ('all', 'player'):
            print("Updating knsb player...")
            refresh_knsb_player(con, args.force)

    print("Done.")
    
if __name__ == '__main__':
    main()
