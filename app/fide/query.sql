CREATE TABLE IF NOT EXISTS fide_rating (
    fide_id INTEGER,
    date TEXT,
    standard_rating INTEGER,
    standard_games INTEGER,
    standard_k INTEGER,
    rapid_rating INTEGER,
    rapid_games INTEGER,
    rapid_k INTEGER,
    blitz_rating INTEGER,
    blitz_games INTEGER,
    blitz_k INTEGER,
    PRIMARY KEY (fide_id, date)
);

INSERT INTO fide_rating
SELECT
    S.ID AS fide_id,
    S.Date AS date,
    S.Rating AS standard_rating,
    S.Gms AS standard_games,
    S.K AS standard_k,
    R.Rating AS rapid_rating,
    R.Gms AS rapid_games,
    R.K AS rapid_k,
    B.Rating AS blitz_rating,
    B.Gms AS blitz_games,
    B.K AS blitz_k
FROM (
    SELECT DISTINCT ID FROM fide_standard
    UNION
    SELECT DISTINCT ID FROM fide_rapid
    UNION
    SELECT DISTINCT ID FROM fide_blitz
) as T, (SELECT DISTINCT Date FROM fide_blitz) as D
LEFT OUTER JOIN fide_standard as S on S.ID = T.ID AND S.Date = D.Date
LEFT OUTER JOIN fide_rapid as R on R.ID = T.ID AND R.Date = D.Date
LEFT OUTER JOIN fide_blitz as B on B.ID = T.ID AND B.Date = D.Date
WHERE S.Date IS NOT NULL;

DROP TABLE fide_standard;
DROP TABLE fide_rapid;
DROP TABLE fide_blitz;

-- A lot of space is left over, so I will just clean it up
VACUUM;
