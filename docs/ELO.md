# The rating of CHESS47

`python3 tools/elo47.py --ladder`: a ladder, every player against every other (8 games a pair, the colours alternating), refereed by python-chess; Stockfish dev-20260930-49ea5ded; CHESS47 is python/chess47ref.py (the same moves as the calculator) with its book. One fit rates them all with Stockfish 1320 fixed (Bradley-Terry); the intervals from 200 refits on resampled games. 2026-11-19, 29 min.

**CHESS47 level 3: about 1276** (95 %: 1194 to 1347), **level 2: about 1145** (95 %: 1055 to 1217), on Stockfish's UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating). Level 3 as searched to the end (on the C47 its time budget can cut it short: then it plays its level-2 move).

| player | rating | 95 % |
|---|---|---|
| Stockfish 1320 | 1320 | 1320 to 1320 |
| Stockfish skill 0, depth 1 | 1307 | 1215 to 1418 |
| Stockfish skill 0, depth 3 | 1293 | 1205 to 1371 |
| CHESS47 level 5, 9 min | 1293 | 1203 to 1371 |
| CHESS47 level 3 | 1276 | 1194 to 1347 |
| CHESS47 level 4, 3 min | 1259 | 1183 to 1342 |
| Stockfish skill 0, 0.1 s | 1254 | 1158 to 1330 |
| CHESS47 level 3, 60 s | 1215 | 1124 to 1290 |
| CHESS47 level 2 | 1145 | 1055 to 1217 |
| CHESS47 level 1 | 918 | 810 to 994 |
| material 2 plies | 771 | 658 to 875 |

|  | Stockfish 1320 | Stockfish skill 0, 0.1 s | Stockfish skill 0, depth 3 | Stockfish skill 0, depth 1 | CHESS47 level 3 | CHESS47 level 5, 9 min | CHESS47 level 4, 3 min | CHESS47 level 3, 60 s | CHESS47 level 2 | CHESS47 level 1 | material 2 plies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Stockfish 1320 | - | 6 | 3 | 3 | 3.5 | 3.5 | 5 | 6 | 8 | 7.5 | 8 |
| Stockfish skill 0, 0.1 s | 2 | - | 1 | 3 | 4 | 5 | 4 | 5.5 | 5.5 | 8 | 8 |
| Stockfish skill 0, depth 3 | 5 | 7 | - | 4 | 4 | 2.5 | 3.5 | 5.5 | 6.5 | 6 | 6.5 |
| Stockfish skill 0, depth 1 | 5 | 5 | 4 | - | 5.5 | 4 | 3.5 | 4.5 | 5 | 7.5 | 8 |
| CHESS47 level 3 | 4.5 | 4 | 4 | 2.5 | - | 4.5 | 4.5 | 5 | 5.5 | 6.5 | 7.5 |
| CHESS47 level 5, 9 min | 4.5 | 3 | 5.5 | 4 | 3.5 | - | 5 | 5 | 5.5 | 7 | 7.5 |
| CHESS47 level 4, 3 min | 3 | 4 | 4.5 | 4.5 | 3.5 | 3 | - | 3.5 | 5 | 7.5 | 8 |
| CHESS47 level 3, 60 s | 2 | 2.5 | 2.5 | 3.5 | 3 | 3 | 4.5 | - | 5 | 7.5 | 8 |
| CHESS47 level 2 | 0 | 2.5 | 1.5 | 3 | 2.5 | 2.5 | 3 | 3 | - | 7.5 | 8 |
| CHESS47 level 1 | 0.5 | 0 | 2 | 0.5 | 1.5 | 1 | 0.5 | 0.5 | 0.5 | - | 6 |
| material 2 plies | 0 | 0 | 1.5 | 0 | 0.5 | 0.5 | 0 | 0 | 0 | 2 | - |

The score of the row's player against the column's (8 games each). The games: `docs/ELO_games.pgn`.
