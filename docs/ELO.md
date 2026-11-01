# The rating of CHESS47

`python3 tools/elo47.py --ladder`: a ladder, every player against every other (8 games a pair, the colours alternating), refereed by python-chess; Stockfish 16; CHESS47 is python/chess47ref.py (the same moves as the calculator) with its book. One fit rates them all with Stockfish 1320 fixed (Bradley-Terry); the intervals from 200 refits on resampled games. 2026-11-01, 21 min.

**CHESS47 level 3: about 1099** (95 %: 982 to 1197), **level 2: about 981** (95 %: 861 to 1071), on Stockfish's UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating). Level 3 as searched to the end (on the C47 its time budget can cut it short: then it plays its level-2 move).

| player | rating | 95 % |
|---|---|---|
| Stockfish skill 0, depth 1 | 1357 | 1238 to 1474 |
| Stockfish skill 0, 0.1 s | 1320 | 1208 to 1443 |
| Stockfish 1320 | 1320 | 1320 to 1320 |
| Stockfish skill 0, depth 3 | 1265 | 1118 to 1381 |
| CHESS47 level 3 | 1099 | 982 to 1197 |
| CHESS47 level 3, 60 s | 1010 | 892 to 1080 |
| CHESS47 level 2 | 981 | 861 to 1071 |
| CHESS47 level 1 | 665 | 526 to 750 |
| material 2 plies | 617 | 488 to 718 |

|  | Stockfish 1320 | Stockfish skill 0, 0.1 s | Stockfish skill 0, depth 3 | Stockfish skill 0, depth 1 | CHESS47 level 3 | CHESS47 level 3, 60 s | CHESS47 level 2 | CHESS47 level 1 | material 2 plies |
|---|---|---|---|---|---|---|---|---|---|
| Stockfish 1320 | - | 6 | 3 | 1 | 8 | 8 | 7 | 8 | 8 |
| Stockfish skill 0, 0.1 s | 2 | - | 5 | 5 | 6.5 | 8 | 6.5 | 8 | 8 |
| Stockfish skill 0, depth 3 | 5 | 3 | - | 3.5 | 4.5 | 6.5 | 7 | 7.5 | 8 |
| Stockfish skill 0, depth 1 | 7 | 3 | 4.5 | - | 7 | 6.5 | 7.5 | 8 | 8 |
| CHESS47 level 3 | 0 | 1.5 | 3.5 | 1 | - | 5 | 7 | 7.5 | 7 |
| CHESS47 level 3, 60 s | 0 | 0 | 1.5 | 1.5 | 3 | - | 4.5 | 8 | 7.5 |
| CHESS47 level 2 | 1 | 1.5 | 1 | 0.5 | 1 | 3.5 | - | 7.5 | 8 |
| CHESS47 level 1 | 0 | 0 | 0.5 | 0 | 0.5 | 0 | 0.5 | - | 5 |
| material 2 plies | 0 | 0 | 0 | 0 | 1 | 0.5 | 0 | 3 | - |

The score of the row's player against the column's (8 games each). The games: `docs/ELO_games.pgn`.
