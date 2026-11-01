# The rating of CHESS47

`python3 tools/elo47.py --ladder`: a ladder, every player against every other (8 games a pair, the colours alternating), refereed by python-chess; Stockfish 16; CHESS47 is python/chess47ref.py (the same moves as the calculator) with its book. One fit rates them all with Stockfish 1320 fixed (Bradley-Terry); the intervals from 200 refits on resampled games. 2026-11-01, 15 min.

**CHESS47 level 2: about 1113** (95 %: 995 to 1218), on Stockfish's UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating).

| player | rating | 95 % |
|---|---|---|
| Stockfish skill 0, depth 1 | 1423 | 1292 to 1564 |
| Stockfish skill 0, depth 3 | 1387 | 1254 to 1540 |
| Stockfish 1320 | 1320 | 1320 to 1320 |
| Stockfish skill 0, 0.1 s | 1263 | 1132 to 1391 |
| CHESS47 level 2 | 1113 | 995 to 1218 |
| CHESS47 level 1 | 892 | 776 to 996 |
| material 2 plies | 718 | 542 to 862 |

|  | Stockfish 1320 | Stockfish skill 0, 0.1 s | Stockfish skill 0, depth 3 | Stockfish skill 0, depth 1 | CHESS47 level 2 | CHESS47 level 1 | material 2 plies |
|---|---|---|---|---|---|---|---|
| Stockfish 1320 | - | 5 | 4 | 1 | 7.5 | 7 | 8 |
| Stockfish skill 0, 0.1 s | 3 | - | 2 | 2 | 6 | 8 | 8 |
| Stockfish skill 0, depth 3 | 4 | 6 | - | 2.5 | 8 | 8 | 8 |
| Stockfish skill 0, depth 1 | 7 | 6 | 5.5 | - | 5 | 7.5 | 7.5 |
| CHESS47 level 2 | 0.5 | 2 | 0 | 3 | - | 7 | 7.5 |
| CHESS47 level 1 | 1 | 0 | 0 | 0.5 | 1 | - | 6.5 |
| material 2 plies | 0 | 0 | 0 | 0.5 | 0.5 | 1.5 | - |

The score of the row's player against the column's (8 games each). The games: `docs/ELO_games.pgn`.
