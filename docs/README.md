# Chess 47 screens and matches

Written by `python3 python/chess47sim.py` (the C47 simulator, 3 pixels per C47 pixel):

- `CHESS47_start.png` the start: the clock, the board, the cursor on e2, the panel
- `CHESS47_play.png` your e2-e4 (5 8 8 5), the C47's reply from its book, the knight on g1 picked (inverted)
- `CHESS47_game.png` the C47 against itself (+ eight times): its book, the move list on the right
- `CHESS47_crazy.png` level 0, CRAZY: random legal moves, the crazy face by the title

`MATCHES.md`: the C47 against a python-chess player, `python3 tools/match47.py`.

The board of the start is checked pixel for pixel against `python/layout.py`'s mock() by `tests/test_chess47.py`.
