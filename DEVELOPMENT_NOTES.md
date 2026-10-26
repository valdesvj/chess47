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

## Oct 25, 2026 - v0.2.0: stronger, the book, the clock, draws, CRAZY (branch claude/chess47-v02)

- The search (chess47ref.ENGINE = mate, recap, mvv; in both twins):
  - MVV: :ADD: puts a capture (code = value taken x 100000 + move) among the captures at the front of its ML row by
    insertion (queen first, the generated order among equals), a quiet move at the back (column 121 - R72): the
    loops read the k-th with :MLK: and no longer need a pass for the captures and one for the others.
  - mate: level 2, a root move that checks (:KATT:), is legal and leaves no legal move (:ANYMV:): 29000.
  - recap: a capture reply is played (:RECAP:) and, when the root side attacks the square, + the value of the piece
    that took it; the quiet replies stay unplayed (:DELTA:).
  Python twins, 20 games from random openings: v0.2 18.5, v0.1 1.5. The back-rank mate and the scholar's mate now
  found. Level 2 is slower: 35-55 s in the middle game (the recaptures' make / unmake and attack tests).
- The book: python/book.py, 14 lines of 10 plies, into the matrix OB (marker REM ==== BOOK); :BOOK: the lines that
  fit the game record (GH row 1), one at random (RAN#).
- The game record GH (2 x 300): the moves (row 1, ply p) and the keys (row 2, p + 1; the start at 1). :HASH:: WSIZE 32,
  the key of a piece ((p + 7) 97 + s) 2654435761 MOD 2^32 (a real, then SINT), XOR, black to move XOR 3141592653,
  →REAL (new command) to store it in the real matrix; the threefold repetition: the key twice before, two plies apart
  (castling and en passant rights not in the key: python-chess counts them, so it can differ in a rare case).
  DRAW: MATERIAL: no pawn, rook or queen and at most one bishop or knight on the board.
- The clock: TICKS, the named variables TK TW TB (tenths of a second); :CLOCK: in the wait (PAUSE 10 now, so it moves
  every second) and before each move; W m:ss B m:ss at the top left. The C47's thinking is counted after its move.
- CRAZY: level 0 (key 1: 2 -> 1 -> 0 -> 2), :CRAZY: a random legal move (from a random place in the list, the first
  that does not leave the king attacked); the face of python/layout.py (marker REM ==== FACE) by the title.
- tools/match47.py: matches in the simulator against a python-chess player (2 plies, material, random among equals),
  keyed with the cursor as a person would; every C47 move checked legal, the board compared after every move, the end
  of every game checked against the rules. docs/MATCHES.md.
- New commands to try on the C47: XOR, →REAL (and AND OR NOT BS?, as Logic 47).

## Oct 25, 2026 - v0.3.0: about 3 times faster, the same moves (branch claude/chess47-speed)

The twin (chess47ref.py) is unchanged: every step below keeps the moves and the values; tests/test_chess47.py all OK
after each one. Steps of :THINK: at level 2 over the three positions of the profile (Kiwipete, an Italian, a closed
Giuoco), 0.17 ms a step: v0.2 872 000 (46-55 s a move), v0.3 about 263 000 (13-19 s). The README has the table.

- Lazy replies (mode 3 of :GEN:, R39 = 3): :ADD: values each reply as it is generated (:QEVAL: quiet, :CEVAL: capture)
  and sets the cut R70 when it refutes the root move; the scan starts on the replying side's own back rank (R99 the
  step +1 / -1), where the pieces that can reply are. The order of the replies does not change the value of the cut.
- :RECAP: values a capture reply without playing it (:DELTA: for SC, the attack test with the from-square emptied for
  the time of the test); :ATT: a tighter ray loop.
- One matrix BD 22 x 120: row 1 the board, 2-4 the move lists (root 2, replies 3, played / ANYMV / TRYMV / CRAZY 4),
  5-17 PT (row piece + 11), 18-20 UN (row ply + 17), 21 the knight masks, 22 the square bits. INDEX "BD" once.
- Knight bitboards: NW NB (named variables, reals: →REAL to store, SINT to recall), bit 8 (row - 2) + col - 1 of the
  square s = 10 row + col + 1. :NUPD: (in :MAKE: after the capture is read, in :UNMK: after the board is restored)
  XORs the bits of a knight that moves or is taken; :NINIT: builds row 22 (the bits, :BIT:) and the words from the
  board (INIT, and the tests' TGEN / TTHK). :ATT: the knight part is mask (row 21) AND the word: 12 steps instead of
  the 8 probes R80-R87. ATT went from 17 % of the time to 12 %. Bit 63 (h8) is negative (2COMPL): the masks are
  written signed by layout.knight_steps(), :BIT: gives -2^63 for h8, so SINT never gets 2^63 or more; c47sim's →REAL
  gives the signed value (marked chess47).
- The scan of :GEN: counted with DSE 31 (as Zones 47): up 78 -> 1 (the square 100 - R31), down 99.021 (IP R31); the
  end test is DSE (one step instead of nine); the cut sets R31 = 0. The piece's kind is in R34 for :GENSQ: and
  :GSLIDE: (R34 is its direction after that). GEN went from 32 900 steps to 24 500.
- Tried and left out: the root moves sorted by a static value (QSORT) before the search: it saved as many steps in the
  replies as it cost. A piece list or occupancy bitboards for the scan: the knight words showed that keeping words up
  to date in every MAKE and UNMK costs about what they save (NUPD 5 400 steps against 15 000 saved in ATT); for the
  occupancy, en passant and castling add updates, and the scan is already 9 % of the time.
- The profile now: GSLIDE 14 %, ATT 12 %, GEN 9 %, ADD 9 %, DELTA 8 %, MAKE 7 %, GSTEP 7 %.
- New commands to try on the C47: →REAL (with a negative word: bit 63). DSE ran in Zones 47; AND OR NOT XOR BS? in
  Logic 47.

## Plans (v0.4)

- A capture search at the leaves, then 3 plies at level 3 when the speed allows.
- Chess960 (Fischer Random): a start position from its number 0-959, castling from any squares (a branch of its own).

## Plans (v0.2): strength (written for v0.1)


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

## Oct 26, 2026 - Out of range on the C47: UNSIGN (branch claude/chess47-unsign)

- The first run on Victor's C47 stopped with Out of range: SINT of 11184810 (the dither, 1010... over 24 bits) at
  WSIZE 24; the C47's default 2COMPL refuses the top bit (also the keys at WSIZE 32, 3141592653). c47sim did not check
  the range: now SINT checks it (UNSIGN 0 .. 2^w - 1, 2COMPL -2^(w-1) .. 2^(w-1) - 1) and →REAL reads the word in the
  mode (marked chess47; to be taken to Almanac 47). Zones 47 and MH-10M 47 stay at WSIZE 64 with small words, so never
  met it.
- Victor's C47: UNSIGN, WSIZE 32, 4294967295 SINT runs (2COMPL after it shows -1: the same 32 bits).
- CHESS47 runs in UNSIGN (INIT) and restores the user's mode: at WSIZE 8, 1 SINT NOT →REAL = 254 / -2 / -1 / -126 for
  UNSIGN / 2COMPL / 1COMPL / SIGNMT, kept in R.09 (LocR 10). The knight masks and :BIT: plain positive again (h8 = 2^63).
- Tests: all OK with the range check; the mode back from 2COMPL and from UNSIGN; 2 matches whole.
