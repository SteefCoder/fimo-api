-- zonder index, limit 10: 0.001s
-- met index, limit 10: 0.011s
SELECT * FROM suggest_player
WHERE full_name LIKE "Carl%" OR
comma_name LIKE "Carl%"
LIMIT 10;

-- zonder index, limit 10: 0.042s
-- met index, limit 10: 0.000s
SELECT * FROM suggest_player
WHERE full_name LIKE "Carlsen,%" OR
comma_name LIKE "Carlsen,%"
LIMIT 10;

-- zonder index, limit 10: 0.192
-- met index, limit 10: 0.000
SELECT * FROM suggest_player
WHERE full_name LIKE "Carlsen, Mag%" OR
comma_name LIKE "Carlsen, Mag%"
LIMIT 10;

-- zonder index, limit 10: 0.002
-- met index, limit 10: 0.003
SELECT * FROM suggest_player
WHERE full_name LIKE "Magn%" OR
comma_name LIKE "Magn%"
LIMIT 10;

-- zonder index, limit 10: 0.188
-- met index, limit 10: 0.000
SELECT * FROM suggest_player
WHERE full_name LIKE "Magnus Ca%" OR
comma_name LIKE "Magnus Ca%"
LIMIT 10;

-- zonder index, limit 10: 0.184
-- met index, limit 10: 0.001
SELECT * FROM suggest_player
WHERE full_name LIKE "Magnus Carl%" OR
comma_name LIKE "Magnus Carl%"
LIMIT 10;
