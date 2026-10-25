# Chess 47 development notes

## Oct 25, 2026 - v0.1.0: the engine (branch claude/chess47-engine)

- The skeleton of Oct 24 (programs/CHESS47.txt, written without a build) could not run: `Date→ℌ` / `Time→ℰ` are
  not C47 commands, `//` lines in the program, a WHILE with no test before it, the standby check reading R57 never
  set, the piece letters chosen by a chain of `X=n?` that push texts. It was rewritten on the pattern of
  Logic 47 / Zones 47: a commented source, tools/build_chess47.py (STRUCT checked and numbered, named labels,
  the glyph marker), python/layout.py, the simulator, tests. The standby check is not there: the hangs of Oct 24
  were a flat CR2032, and a running PAUSE / KEY? loop does not go to standby on the C47.
- Board: BD 1 x 120, the 10 x 12 mailbox, s = 10 row + col + 1 (rows 0-11, cols 0-9): a1 22, h1 29, a8 92, h8 99.
  The border is 8: for a colour c, x = piece x c is 1-6 for its own pieces (|x - 3.5| <= 2.5), -1..-6 for the
  other's (|x + 3.5| <= 2.5), and the border gives +-8: one ABS and one test for each class, with no test of
  its own for the border.
- Moves: from x 1000 + to. :GEN: scans 22-99, then per piece :GPAWN: (+ :PCAP: the captures and en passant),
  :GSTEP: (knight R80-R87, king R88-R95), :GSLIDE: (R88-R91 diagonals, R92-R95 lines), :GCAST: (the bits 1 - c and
  2 - c of the castling word with BS? IND, the squares empty and not attacked: :ATT:). The order is that of
  chess47ref.gen, so the lists are equal.
- :MAKE: / :UNMK: at a ply (1 the search root, 2 unused now, 3 a played move): UN row (move, piece, taken, ep, SC,
  flag), R56 + ply the castling word (a short integer: kept in a register, not in the real matrix). SC by the
  values of PT (13 x 99, row piece + 7). Promotion to a queen; en passant; castling with the rook (:ROOKS:);
  the castling rights by AND with 1100 1101 1110 0011 0111 1011 (#2) when e1 a1 h1 e8 a8 h8 is touched (:CRSQ:).
- :THINK: the root moves in ML row 1, captures first (a pass for the captures, one for the others, each in the
  order generated); level 1 (:LEGAL1:: the king attacked -> -30000) or level 2 (:REPLY:: the replies in ML row 2,
  not played: :DELTA: gives S x (SC + their change), the least, a cut as soon as it is <= the best). No legal
  move: best < -10000 (the king is lost in every line).
- The start: the PT table by square (:PSQ: the geometry once, the six kinds, the black value on the mirror square
  s + 10 (11 - 2 row)), the glyphs (:GLYPHS:: dither AND NOT mask OR glyph, WSIZE 24), the 64 squares (:DRAWSQ:
  GRMOD 1, 24 AGRAPH columns), the letters, the panel: 58 000 steps, about 10 s on the C47.
- Times (0.17 ms a step): a move of the C47 at level 2 20-45 s in the middle game, level 1 1-10 s.
  Profile of a move: the generator about 60 % (the scan of 78 squares a ply, the probes), make / unmake 20 %.
- Tests: tests/test_chess47.py (see its header). chess47ref: perft 20 / 400 / 8 902 / 197 281 (start), Kiwipete
  48 / 2 039 / 97 862, position 3 14 / 191 / 2 812 / 43 238, positions 4 and 5 with the under-promotions left out
  (as python-chess's counts without them).

## Plans (v0.2): strength

The limit on a calculator is speed: work the firmware does in one command beats hundreds of RPN steps.

1. Mate in the search: the back-rank mate `6k1/5ppp/8/8/8/8/5PPP/3R2K1 w` is missed at level 2 (the replies
   that leave the king in check are not filtered: depth 3). A check at the root: a move after which the other
   side has no legal move (:ANYMV:) and is in check scores a mate.
2. A capture search at the leaves (quiescence), MVV-LVA ordering (more cuts): the horizon blunders, then 3 plies.
3. 64-bit bitboards next to the matrix: attack tests with AND / OR, pawn structure (doubled, isolated, passed)
   with masks; Zobrist keys (XOR) for repetitions and a small transposition table.
4. The board as a 64-vector: the evaluation as one DOT with a piece-square vector (native speed).
5. An opening book in a matrix.
6. The generator: a list of the pieces' squares instead of the scan of 78 squares.
EIGEN and the 34-digit precision do not help a chess engine: not planned.
