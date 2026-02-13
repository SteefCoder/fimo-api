CREATE INDEX IF NOT EXISTS idx_fide_match
ON fide_player (name, fed, birthyear, sex);

CREATE INDEX IF NOT EXISTS idx_knsb_match
ON knsb_player (name, fed, birthyear, sex);

UPDATE knsb_player
SET fide_id = (
    SELECT fp.fide_id
    FROM fide_player fp
    WHERE knsb_player.name = fp.name
      AND knsb_player.fed = fp.fed
      AND knsb_player.birthyear = fp.birthyear
      AND knsb_player.sex = fp.sex
)
WHERE fide_id IS NULL
AND (
    SELECT COUNT(*)
    FROM fide_player fp
    WHERE knsb_player.name = fp.name
      AND knsb_player.fed = fp.fed
      AND knsb_player.birthyear = fp.birthyear
      AND knsb_player.sex = fp.sex
) = 1;