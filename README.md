# Chess 47 ♟️

A chess engine for the **C47 / R47** RPN calculator (and the DM42n with the C47 firmware): you play against the
calculator on its own screen. As far as I know, the first chess engine for the C47.

![the start](docs/CHESS47_start.png)

The engine follows the idea of the "matrix" mini engines (Micro-Max, H.G. Muller). The board is a matrix, the
10 × 12 mailbox, and the engine works from it: the move generator, check and mate, and a 2-ply alpha-beta search
with a score kept up to date by every move.

| | |
|---|---|
| File | `build/CHESS47.txt` (convert with rejig), commented: `build/forum/CHESS47.p47u`, source: `programs_rem/CHESS47.txt` |
| Needs | C47 / R47 firmware with STRUCT, ATEXT, GRFNT, AGRAPH and the bitwise commands (00.109.05.00a0.ALPHA, 5 Oct 2026, or later) |
| Size | 3 368 steps, about 10 KB (.p47, estimated); while it runs the matrices BD, PT, ML, UN, GL (about 2 900 numbers) |
| At the end (0) | your stack and LASTx as before; R00-R19 untouched, R20-R99 cleared; the matrices deleted; WSIZE 64, GRMOD 0, GRFNT 20 |

## Playing

`XEQ "CHESS47"`. Setting up takes about 10 s (the tables and the board). You have the white pieces.

| Key | |
|---|---|
| **8 2 4 6** | the cursor up, down, left, right |
| **5** | pick a piece of yours (its square is inverted), then **5** on the square to play it; 5 on the same square drops it |
| **+** | the C47 plays the side to move (you take the other side): press it at the start to play black, or to watch |
| **1** | the level: 2 (2 plies, about 20-45 s a move) or 1 (1 ply, a few seconds) |
| **0** | the end |

The rules are all there: castling (not out of, through or into check), en passant and promotion (always to a queen).
CHECK, CHECKMATE and STALEMATE are shown. There are no draws by repetition or by the 50-move rule. An illegal move is
refused (ILLEGAL MOVE, or ILLEGAL: CHECK when it leaves your king attacked). The last eight moves are listed on the right.

![a game](docs/CHESS47_game.png)

**Strength:** about 800-1100 Elo by my estimate (it has not been measured). It sees one-move tactics, but at 2 plies
it misses deeper ones and does not see a mate in one yet.

## How it works

- **The board:** a 1 × 120 matrix BD, the 10 × 12 mailbox (a1 = 22 … h8 = 99, the border 8). A piece is 1-6
  (pawn, knight, bishop, rook, queen, king), positive for white and negative for black. A move is from × 1000 + to.
- **The score:** a matrix PT (13 × 99) holds the signed value of each piece on each square (material + a piece-square
  table). Each move updates SC from three or four lookups, and SC is never recomputed.
- **The moves of a ply** go into a row of the matrix ML, and the undo data into a row of UN.
- **The search:** 2 plies with alpha-beta cuts, captures first. A move that lets the king be taken scores
  about -20000, so the search never chooses one. The replies are not played: their effect on SC is worked out
  directly.
- **The 64-bit bitwise commands:**
  - the castling rights are one 4-bit word (`AND` clears a right, `BS?` tests one);
  - the dark squares are computed from the glyphs: dither `AND NOT` mask `OR` glyph (WSIZE 24, a 24-pixel column is one
    `AGRAPH` word), so only one set of glyphs is stored.
- **Not used:** EIGEN and the 34-digit precision don't make a chess engine stronger, so they are not forced in.
  The plans for more strength are in `DEVELOPMENT_NOTES.md`: bitboards, a capture search, mate detection, an opening book.

## Tested

In the C47 simulator only (`python/c47sim.py`, from Almanac 47), with `python3 tests/test_chess47.py`. The test checks
against `python/chess47ref.py`, the same engine in Python:

- the move generator gives the same moves, in the same order, for 12 positions: castling, en passant, promotion, pins;
- the reference generator gives the published perft counts (20 / 400 / 8 902 / 197 281 from the start, Kiwipete,
  position 3), with promotions to a queen only;
- the search gives the same move and value at levels 1 and 2;
- a game of the C47 against itself is move for move the same, with the same board and score;
- moves keyed with 5 and the arrows work, and illegal moves are refused;
- the start screen matches `python/layout.py`'s picture pixel for pixel.

**Not yet run on a real C47.** `AND`, `OR`, `NOT` and `BS?` are new to these projects: they are used in Logic 47,
which is also still to be run on the calculator.

## Files

| | |
|---|---|
| `programs_rem/CHESS47.txt` | the commented source (STRUCT, named labels) |
| `tools/build_chess47.py` | writes `programs/`, `build/` and `listings/`, and `build/forum/CHESS47.p47u` |
| `python/layout.py` | the board's place, the piece glyphs (the build writes their words into the program) |
| `python/chess47ref.py` | the engine in Python, step for step as the program, and perft |
| `python/chess47sim.py` | runs the program in the simulator and writes the screens in `docs/` |
| `python/c47sim.py`, `stdfont.py`, `tinyfont.py` | the C47 simulator and fonts, from Almanac 47; the bitwise commands from Logic 47 |
| `tests/test_chess47.py` | the tests above |

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros. Written with the help of AI. See `AI_ASSISTANCE.md` for
the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator
community.
