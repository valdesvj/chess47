# Chess 47 screens

Written by `python3 python/chess47sim.py` (the C47 simulator, 3 pixels per C47 pixel):

- `CHESS47_start.png` the start: the board, the cursor on e2, the panel
- `CHESS47_play.png` your e2-e4 (5 8 8 5), the C47's reply, the knight on g1 picked (inverted)
- `CHESS47_game.png` the C47 against itself (+ eight times): the move list on the right

The board of the start is checked pixel for pixel against `python/layout.py`'s mock() by `tests/test_chess47.py`.
