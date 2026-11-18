# The rating of CHESS47

`python3 tools/elo47.py --ladder`: a ladder, every player against every other (8 games a pair, the colours alternating), refereed by python-chess; Stockfish dev-20260930-49ea5ded; CHESS47 is python/chess47ref.py (the same moves as the calculator) with its book. One fit rates them all with Stockfish 1320 fixed (Bradley-Terry); the intervals from 200 refits on resampled games. 2026-11-19, 33 min.

**CHESS47 level 3: about 1325** (95 %: 1245 to 1412), **level 2: about 1071** (95 %: 1002 to 1145), on Stockfish's UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating). Level 3 as searched to the end (on the C47 its time budget can cut it short: then it plays its level-2 move).

| player | rating | 95 % |
|---|---|---|
| Stockfish skill 0, 0.1 s | 1325 | 1232 to 1422 |
| CHESS47 level 3 | 1325 | 1245 to 1412 |
| Stockfish 1320 | 1320 | 1320 to 1320 |
| Stockfish skill 0, depth 3 | 1311 | 1224 to 1406 |
| CHESS47 level 5, 9 min | 1307 | 1230 to 1372 |
| CHESS47 level 4, 3 min | 1271 | 1185 to 1354 |
| Stockfish skill 0, depth 1 | 1267 | 1174 to 1349 |
| CHESS47 level 3, 60 s | 1262 | 1193 to 1346 |
| CHESS47 level 2 | 1071 | 1002 to 1145 |
| CHESS47 level 1 | 933 | 835 to 1019 |
| material 2 plies | 790 | 706 to 869 |

|  | Stockfish 1320 | Stockfish skill 0, 0.1 s | Stockfish skill 0, depth 3 | Stockfish skill 0, depth 1 | CHESS47 level 3 | CHESS47 level 5, 9 min | CHESS47 level 4, 3 min | CHESS47 level 3, 60 s | CHESS47 level 2 | CHESS47 level 1 | material 2 plies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Stockfish 1320 | - | 4 | 2 | 2 | 3.5 | 5 | 5.5 | 6 | 8 | 8 | 8 |
| Stockfish skill 0, 0.1 s | 4 | - | 5 | 3 | 5.5 | 5 | 5.5 | 4.5 | 6 | 6 | 8 |
| Stockfish skill 0, depth 3 | 6 | 3 | - | 4 | 2.5 | 4 | 4 | 4.5 | 7.5 | 7.5 | 8 |
| Stockfish skill 0, depth 1 | 6 | 5 | 4 | - | 3.5 | 1 | 0.5 | 4.5 | 7.5 | 6 | 8 |
| CHESS47 level 3 | 4.5 | 2.5 | 5.5 | 4.5 | - | 5 | 5 | 4.5 | 7 | 6.5 | 7.5 |
| CHESS47 level 5, 9 min | 3 | 3 | 4 | 7 | 3 | - | 6 | 4.5 | 6 | 7 | 7 |
| CHESS47 level 4, 3 min | 2.5 | 2.5 | 4 | 7.5 | 3 | 2 | - | 4.5 | 6 | 6.5 | 8 |
| CHESS47 level 3, 60 s | 2 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | - | 6.5 | 8 | 8 |
| CHESS47 level 2 | 0 | 2 | 0.5 | 0.5 | 1 | 2 | 2 | 1.5 | - | 8 | 7.5 |
| CHESS47 level 1 | 0 | 2 | 0.5 | 2 | 1.5 | 1 | 1.5 | 0 | 0 | - | 5 |
| material 2 plies | 0 | 0 | 0 | 0 | 0.5 | 1 | 0 | 0 | 0.5 | 3 | - |

The score of the row's player against the column's (8 games each). The games: `docs/ELO_games.pgn`.
