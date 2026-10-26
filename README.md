# Chess 47 ♟️

A chess engine for the **C47 / R47** RPN calculator (and the DM42n with the C47 firmware): you play against the
calculator on its own screen. As far as I know, the first chess engine for the C47.

![the start](docs/CHESS47_start.png)

The engine follows the idea of the "matrix" mini engines (Micro-Max, H.G. Muller). The board is a matrix, the
10 × 12 mailbox, and the engine works from it: the move generator, check and mate, and a 2-ply alpha-beta search
with a score kept up to date by every move. v0.2 adds mate detection, the recapture after a capture and the
biggest captures first (it beat v0.1 18.5 to 1.5 in 20 games), an opening book, a chess clock, draws by
repetition and by material, and a CRAZY level of random moves. v0.3 plays the same moves about 3 times faster (a
move at level 2 about 13-19 s instead of 46-55 s, in the simulator's step count): see *Speed* below.

| | |
|---|---|
| File | `build/CHESS47.txt` (convert with rejig), commented: `build/forum/CHESS47.p47u`, source: `programs_rem/CHESS47.txt` |
| Needs | C47 / R47 firmware with STRUCT, ATEXT, GRFNT, AGRAPH and the bitwise commands (00.109.05.00a0.ALPHA, 5 Oct 2026, or later) |
| Size | 5 411 steps, about 16 KB (.p47, estimated); while it runs the matrices BD, GL, GH, OB (about 4 200 numbers) and the variables NW NB |
| At the end (0) | your stack and LASTx as before; R00-R19 untouched, R20-R99 cleared; the game kept for the next start (the variables CHN, GH, TW, TB); the other matrices, TK and the knight words NW NB deleted; WSIZE 64, your integer mode back, GRMOD 0, GRFNT 20 |

## Playing

`XEQ "CHESS47"`. Setting up takes about 10 s (the tables and the board). You have the white pieces; a game left with
**0** goes on where it was (the moves played again: a few seconds more).

| Key | |
|---|---|
| **8 2 4 6** | the cursor up, down, left, right |
| **5** | pick a piece of yours (shown white on black, on light and dark squares), then **5** on the square to play it; 5 on the same square drops it |
| **+** | swap sides: the C47 plays the side to move and you take the other; at the start: you play black (the board turns, black at the bottom) |
| **9** | C47 vs C47: it plays both sides until checkmate or a draw; any key stops it and you take the side to move (0 ends) |
| **7** | a new game (the level and your side kept) |
| **1** | the level: 2 (2 plies, about 10-20 s a move), 1 (1 ply, a few seconds), 0 **CRAZY** (random legal moves at once, a crazy face by the title) |
| **0** | the end; the game is kept and goes on at the next start (not when it is over) |

The rules are all there: castling (not out of, through or into check), en passant and promotion (always to a queen).
CHECK, CHECKMATE, STALEMATE, DRAW: REPETITION (the same position the third time, the same side to move) and DRAW: MATERIAL
(kings only, or one bishop or knight) are shown; there is no 50-move rule. An illegal move is refused (ILLEGAL MOVE, or
ILLEGAL: CHECK when it leaves your king attacked). The last seven moves are listed on the right. The clock at the top
left counts each side's time (TICKS, the time of the side to move; it stops when the game is over).

The C47 opens from its book (python/book.py: 14 main lines, Ruy Lopez to Réti, 10 plies each) as long as the game
follows one of them, choosing at random among those that fit; then it thinks.

![a game](docs/CHESS47_game.png)

**Strength:** v0.1 by my estimate about 800-1100 Elo; v0.2 beat v0.1 18.5-1.5 in 20 games (the Python twins), so
perhaps 1100-1300. Not measured against rated players. It sees mates in one, one-move tactics and the recapture; it
misses deeper tactics. The matches against an independent player in the simulator: `docs/MATCHES.md`.

![crazy](docs/CHESS47_crazy.png)

## How it works

- **One matrix BD (22 × 120)** holds everything the search reads, so it never switches INDEX:
  - row 1, the board: the 10 × 12 mailbox (a1 = 22 … h8 = 99, the border 8). A piece is 1-6 (pawn, knight, bishop,
    rook, queen, king), positive for white and negative for black. A move is from × 1000 + to;
  - rows 2-4, the move lists (the root, the replies, the moves played);
  - rows 5-17, the score table PT: the signed value of each piece on each square (material + a piece-square table).
    Each move updates SC from three or four lookups, and SC is never recomputed;
  - rows 18-20, the undo data of each ply;
  - rows 21-22, the knight masks and the bit of each square (below).
- **The search:** 2 plies with alpha-beta cuts. The moves come out of the generator ordered: the captures by the
  value taken, queen first (an insertion as they are added), then the others. A move that lets the king be taken
  scores about -20000, so the search never chooses one. A checking move after which the other side has no legal
  move is a mate (29000). A capture reply is played and answered by its recapture when the square is attacked;
  the other replies are not played: their effect on SC is worked out directly. The replies are valued as they are
  generated, starting from the replying side's own back rank, and the generator stops at the first one that refutes.
- **The 64-bit bitwise commands:**
  - the castling rights are one 4-bit word (`AND` clears a right, `BS?` tests one);
  - the dark squares are computed from the glyphs: dither `AND NOT` mask `OR` glyph (WSIZE 24, a 24-pixel column is one
    `AGRAPH` word), so only one set of glyphs is stored;
  - each position after a move gets a 32-bit key, Zobrist style: one word for each piece on its square, `XOR`ed together
    (WSIZE 32); the keys of the game (the matrix GH, with `→REAL`) find the threefold repetition;
  - the knights of each side are a 64-bit word (NW, NB: bit 8 (rank - 1) + file - 1), kept by every move and its
    take-back with `XOR`; "is this square attacked by a knight" is one `AND` with the square's knight mask (row 21 of BD)
    instead of eight probes.
- **The other matrices:** the glyphs GL, the game record GH (moves and keys), the opening book OB.
- **Not used:** EIGEN and the 34-digit precision don't make a chess engine stronger, so they are not forced in.
  The plans are in `DEVELOPMENT_NOTES.md`.

## Speed (v0.3)

The same moves and the same values as v0.2 (the Python twin is unchanged), counted in simulator steps over three
middle-game positions at level 2 (0.17 ms a step on the C47):

| | steps | a move |
|---|---|---|
| v0.2 | 872 000 | 46-55 s |
| the replies valued as generated, from their own side, the cut at the first refutation | 296 000 | |
| the capture replies valued without being played; a tighter ray loop for the attack test | 283 000 | |
| one matrix BD for the board, the lists, PT and the undo data (no INDEX switching) | 279 000 | |
| the knight attack test with bitboards (`AND`), the square bits read from a table | 270 000 | |
| the scan of the squares counted with `DSE` (the end test one step instead of nine) | 262 000 | |
| **v0.3** (h8's bit kept signed, below) | **263 000** | **13-19 s** |

Tried and left out, as they cost as much as they saved: sorting the root moves before the search (`QSORT`), and a list
of the pieces or occupancy bitboards for the scan (keeping them up to date in every move and take-back costs about what
the scan saves).

## Tested

In the C47 simulator only (`python/c47sim.py`, from Almanac 47), with `python3 tests/test_chess47.py`. The test checks
against `python/chess47ref.py`, the same engine in Python:

- the move generator gives the same moves, in the same order, for 12 positions: castling, en passant, promotion, pins;
- the reference generator gives the published perft counts (20 / 400 / 8 902 / 197 281 from the start, Kiwipete,
  position 3), with promotions to a queen only;
- the search gives the same move and value at levels 1 and 2 (mates in one found);
- a game of the C47 against itself: the book moves are from its lines, then move for move the same, with the same
  board and score; 20 CRAZY moves all legal; the clock runs;
- 10 matches against an independent python-chess player (`tools/match47.py`): every move legal, the board right
  after every move, every game ended as the rules say;
- moves keyed with 5 and the arrows work, and illegal moves are refused; the cursor and the piece picked show on a
  dark square; + turns the board; 9 plays on until a key; a game left with 0 comes back the same; 7 starts again;
- the start screen matches `python/layout.py`'s picture pixel for pixel.

**The integer mode.** CHESS47's words are bit patterns: the repetition keys up to 2^32 (WSIZE 32), the glyph columns
up to 2^24 (WSIZE 24), the knight words up to 2^64. In `2COMPL`, the C47's default, `SINT` refuses a value with the
top bit set (**Out of range**: the error of the first run on the calculator, Oct 26). So CHESS47 runs in `UNSIGN`
(Victor's C47: `UNSIGN` `WSIZE 32` `4294967295 SINT` runs) and gives you back your own mode at the end: at the start it
reads it (at WSIZE 8, `1 SINT NOT →REAL` is 254 in UNSIGN, -2 in 2COMPL, -1 in 1COMPL, -126 in SIGNMT) and keeps it in
the local register R.09. The simulator now refuses SINT out of range as the C47 does.

`AND`, `OR`, `NOT`, `XOR`, `BS?` ran on the calculator in Logic 47, `UNSIGN` / `2COMPL` on Victor's C47; `→REAL`,
`1COMPL` and `SIGNMT` are still to be confirmed there. `0 STO+ "CHN"` (it creates the variable the first time) ran in
Almanac 47's MOON47.

## Files

| | |
|---|---|
| `programs_rem/CHESS47.txt` | the commented source (STRUCT, named labels) |
| `tools/build_chess47.py` | writes `programs/`, `build/` and `listings/`, and `build/forum/CHESS47.p47u` |
| `build/forum/CHESS47.p47u` | the commented file for the forum and the C47's PROGRAMS folder: how to use it in plain words, then the code with its comments in `@` lines (rejig does not compile them: no REM steps); its narrative is `tools/forum/CHESS47.txt` |
| `tools/build_p47.py` | on your computer with rejig: `build/p47/CHESS47.p47` from the forum file (`--validate=r47`), checked byte for byte against the plain listing's |
| `python/layout.py` | the board's place, the piece glyphs, the crazy face (the build writes their words into the program) |
| `python/book.py` | the opening book (the build writes it into the matrix OB) |
| `tools/match47.py` | matches in the simulator against a python-chess player, written to `docs/MATCHES.md` |
| `python/chess47ref.py` | the engine in Python, step for step as the program, and perft |
| `python/chess47sim.py` | runs the program in the simulator and writes the screens in `docs/` |
| `python/c47sim.py`, `stdfont.py`, `tinyfont.py` | the C47 simulator and fonts, from Almanac 47; the bitwise commands from Logic 47 |
| `tests/test_chess47.py`, `tests/test_forum.py` | the tests above; the forum file (its steps = the listing's, no REM, the narrative) |

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros. Written with the help of AI. See `AI_ASSISTANCE.md` for
the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator
community.
