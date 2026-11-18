# Influence maps for CHESS47: a test in Python (branch claude/chess47-influence)

Victor's question (Nov 18, 2026): would an 8 × 8 "influence matrix" engine play stronger? Before any RPN is written,
the influence maps were added to the twin (`python/influence.py`, a subclass of `python/chess47ref.py`, which stays
unchanged) and played against CHESS47 as it is with `tools/influence47.py`: 355 openings (the book's lines cut after
4-10 plies and 300 openings of 4 random plies, seed 47), each played with both colours, every move refereed by
python-chess, a draw after 200 plies. 710 games a line.

**The maps:** for each square, how many pieces of each side attack it and the cheapest one. **The terms**, seen from
the side S that searches: square control (a square counts for the side with more attackers: 4 for d4 e4 d5 e5, 2 for
the 12 around them, 5 for the squares around the other king, 1 else; x C_ALL), and threats (a piece attacked and not
defended, or attacked by a cheaper piece). **Leaf:** the maps at every leaf of level 2 (after S's move and the reply).
**Root:** once after each of S's moves, the same term for all its replies (about 6 times fewer maps).

## Results (rating difference against the plain twin; 95 % from the paired games)

| the influence engine | against | score | difference | 95 % |
|---|---|---|---|---|
| leaf, C_ALL 1 | level 2 | 58.3 % | **+58** | +39 to +77 |
| root, C_ALL 1 | level 2 | 59.2 % | **+64** | +44 to +85 |
| root, C_ALL 2 (the default now) | level 2 | 61.2 % | **+79** | +57 to +101 |
| root, C_ALL 2, no fork term | level 2 | 61.1 % | +78 | +58 to +99 |
| root, C_ALL 3 | level 2 | 59.7 % | +68 | +48 to +88 |
| root, no control (threats only) | level 2 | 51.4 % | +9 | -8 to +28 |
| root, fork term x 2 (T_FORK 1.5) | level 2 | 40.0 % | -70 | -91 to -49 |
| root, C_ALL 2 | **level 3** (to the end) | 27.3 % | **-170** | -189 to -152 |

What it says:
- The gain is real but modest: about **+80 at level 2** (about 1060 on docs/ELO.md's scale, where level 2 is 981).
  It comes from **square control** (the king zone and the centre); the threat terms add nothing or hurt.
- **Depth is worth far more:** plain level 3 beats the best influence level 2 by about 170 points.
- The weights were chosen on the same openings, so +79 is a little optimistic.

## The cost on the C47

A map of both sides is about the work of two full move generations: a full GEN of one side is about 4 600 steps in the
simulator (8 300 with NINIT, 35 moves), so a map with the square counts in a matrix row is about 9 000-11 000 steps.
The root variant builds about 29-31 maps a move, the leaf variant about 175.

| | maps a move | extra steps a move (estimate) | a level-2 move on the C47 (now 6-11 s) |
|---|---|---|---|
| root | ~30 | ~300 000 | about 35-65 s (5-6 x) |
| leaf | ~175 | ~1 700 000 | several minutes |

So on the C47 the root variant would cost about what level 3 costs (up to 60 s) for less than half its gain. An 8 × 8
board would save about 10 KB more RAM (the move lists in their own 3 × 120 matrix) but loses the mailbox's border, so
the move generator needs off-board tests and gets slower; with the maps the start would need about 32 KB (47.8 KB on
claude/chess47-opt).

**Recommendation:** not worth porting to RPN as it stands. If it is tried, the root variant with the control term
only (the cheapest), or the control term inside level 3's leaves when there is time left. For chess47.pg5 (C, with
quiescence, mobility and a transposition table already), the control idea maps to a king-zone attack term; worth tens
of Elo there at most, and it costs nodes a second.

## Found on the way: illegal king moves (CHESS47 v0.6.0 / v0.7.0)

The recapture rule of level 2 (a capture reply on a square S attacks: + the value of the piece that took) also applies
when the reply is the other king taking S's king, and adds that king's 20 000: the king's loss cancels out, so a king
move next to the other king, onto a square S defends, can look legal. The twin and the C47 program (simulator) both
play it, for example:

| position | move played |
|---|---|
| `2n5/3B4/2K5/k1N5/8/8/8/Q7 b - - 0 1` | Ka5-b6 (next to Kc6) |
| `8/4B3/8/8/7Q/4P1K1/5q2/4k3 w - - 0 1` | Kg3xf2 (next to Ke1) |
| `1R6/3b4/6N1/5k1K/8/8/8/7B b - - 0 1` | Kf5-g4 (next to Kh5) |

The fix: no recapture bonus when the reply took the king. Done in v0.7.1 (branch claude/chess47-kingrecap, LBL :RECAP:
and the twin), merged into this branch; `python/influence.py` had it already, so the results above are unchanged.
