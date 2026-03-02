DROP TABLE IF EXISTS suggest_player;

CREATE TABLE suggest_player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knsb_id INTEGER,
    fide_id INTEGER,
    comma_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    FOREIGN KEY (knsb_id) REFERENCES knsb_player,
    FOREIGN KEY (fide_id) REFERENCES fide_player
);

CREATE INDEX s_knsb_idx ON suggest_player (knsb_id);
CREATE INDEX s_fide_idx ON suggest_player (fide_id);
CREATE INDEX s_comma_idx ON suggest_player (comma_name COLLATE NOCASE);
CREATE INDEX s_full_idx ON suggest_player (full_name COLLATE NOCASE);

INSERT INTO suggest_player (knsb_id, fide_id, comma_name, full_name)
SELECT
    kp.knsb_id,
    fp.fide_id,
    COALESCE(kp.name, fp.name),
    SUBSTR(COALESCE(kp.name, fp.name), INSTR(COALESCE(kp.name, fp.name), ',') + 2) || ' ' ||
    SUBSTR(COALESCE(kp.name, fp.name), 1, INSTR(COALESCE(kp.name, fp.name), ',') - 1)
FROM knsb_player kp
FULL OUTER JOIN fide_player fp
ON kp.fide_id = fp.fide_id;
