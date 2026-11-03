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

## Oct 26, 2026 - v0.3.1: the cursor on dark squares, black, C47 vs C47, the game kept (branch claude/chess47-play)

Victor on the C47: the cursor and the piece picked did not show on a dark square (a XOR frame and an inversion of the
dither look like the dither); + was not seen as playing black (the board stayed white's); 0 lost the game; a C47 vs
C47 mode until mate.
- :DRAWSQ: draws the cursor (R28: a frame OR'd, 2 pixels) and the piece picked (R29: the light square's row, NOT)
  itself; :CURS: is one DRAWSQ; :SELX: gone. A plain square keeps the old loop (the tests cost only the 2 squares).
- The board seen from your side: :SQXY: mirrors file and rank when R27 = -1; :BOARD: (the squares, a-h and 1-8 the
  other way round); :SETME: X = your new side: the board drawn again only when black's / white's view changes, the
  cursor to e2 / e7.
- 9: R27 = 0, the C47 plays both sides; after each of its moves 0 PAUSE 1 KEY? 98: a key: you take the side to move
  (0 ends). At the game's end the usual wait (0, 7).
- The game kept: at 0, CHN = plies x 100 + level x 10 + side + 2 with GH TW TB (the plies 2 (R96 - 1) + (1 - R20) / 2,
  at most 299; a finished game keeps only level and side). The start: 0 STO+ "CHN" (MOON47's way), the plies played
  again with MAKE, GHADD, HTEXT (HIST without drawing), then the board drawn once. 7: CHN without plies, INIT again.
- c47sim: a key None = no key at that KEY? (the C47 vs C47 tests); chess47sim.run(mats=) for the kept game.

## Oct 26, 2026 - the forum file for new users (branch claude/chess47-forum)

- The forum (the C47's PROGRAMS folder): each contributed program should say in plain words what it does and how to
  use it, in '@' lines (not "#": rejig makes a '#' line a REM step), and use local labels. build_forum.py: after the
  '@' metadata, tools/forum/CHESS47.txt (What it is, How to use it, What it changes on your calculator, Programs and
  labels), then the source's header as technical notes; the source's comment blocks as whole '@' lines before their
  steps (before: cut into pieces after ';' on the following steps), the label names after ';'.
- tools/build_p47.py (Victor runs it with rejig): build/p47/CHESS47.p47 from the forum file, --validate=r47, the same
  bytes as from the plain listing. tests/test_forum.py.

## Oct 26, 2026 - v0.3.2: pieces drawn off the board, the 5-minute clock (branch claude/chess47-clock)

- Victor's C47 after a 239-move CRAZY game: black rooks drawn right of the board, over the move list. :PLAYED: called
  :GHADD: first, and its :HASH: counts the pieces other than the kings in R47; :PLAYED: then read R47 as MAKE's flag
  (1 en passant, 2 castling): with one or two pieces left an ordinary move redrew a captured pawn's or a rook's
  squares, h-file moves the border (8, drawn as row 15 of GL: a black rook on a dark square). Since v0.2. Now the
  squares are drawn first, GHADD after. Test: h2-h3 with a rook and a pawn (the old build: 91 pixels off the board).
- The clock (Victor): 5 minutes each, 10 s more a move (Fischer); TW TB are the time left (3000 tenths at the start),
  :CLOCK: takes the time off the side to move and at 0 or less: WHITE / BLACK LOST ON TIME (R97); :PLAYED: adds 100
  to the side that moved; :C47MV: plays no move when its time ran out while it thought. TK is set at the end of INIT
  (the setting up was white's time). A game saved by v0.3.1 has its used time in TW TB: read as the time left.
- The time-out as FIDE 6.9 (Victor): a draw when the opponent cannot mate by any series of legal moves. :TMAT: is
  python-chess's has_insufficient_material(w) (a knight: w's only piece and the other side only king and queens;
  bishops: all on one colour, no pawn or knight; a bare king), checked on 300 random positions of few pieces.
  DRAW: TIME, NO MATE. TRYMV too plays no move when the time ran out.
- Victor: the clock only for people (the C47 at level 2 thinks 10-25 s, more than the 10 s a move: it lost on time in
  long games). :HUMQ: X = a colour: a person plays it (R27, or R27 = 2 both); :CLOCK: charges nothing to the C47's
  side, :PLAYED: gives the 10 s only to a person. Two players (key 3, R27 = 2): :HUMAN: for both sides, WHITE /
  BLACK TO MOVE, the board white's; + from there gives the side to move to the C47. The status line is cleared over
  184 pixels (23 spaces; was 128: DRAW: TIME, NO MATE is 179). The keys on four lines.
- tools/selfplay47.py (run by Victor with python-chess): the C47 against itself, 5 games a level; python-chess
  checks every move, the board, every end and the clock. docs/SELFPLAY.md.

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

## Oct 26, 2026 - Invalid input data type: STOEL of a short integer (branch claude/chess47-stoel)

- With UNSIGN the C47 (Victor's simulator) went past the SINTs and stopped in :GLYPHS: at STOEL: the glyph word
  (5 592 405, a short integer) into the real matrix GL: "Invalid input data type for this operation". Now →REAL
  before the STOEL (UNSIGN: the word's value, positive); :DRAWSQ: reads it with RCLEL SINT as before.
- c47sim keeps the type: SINT and AND OR XOR NOT give a short integer (class SI), →REAL a real; STOEL refuses a short
  integer as the C47 (marked chess47; to be taken to Almanac 47). Scanned over the whole test run: no other command
  gets a short integer except SINT, →REAL, the bitwise ones, AGRAPH and the stores.

## Nov 1, 2026 - v0.3.3: the move list in standard algebraic notation (branch claude/chess47-san)

- Victor: the list showed e5d4 (no capture, no piece). Now SAN as FIDE's Appendix C: e4, Nf3, exd5, Nbd2, R1e2, Qh1e4,
  O-O, O-O-O, e8=Q, Qh7+, Ra8#. :HTEXT: reads the move from the undo row of ply 3 (row 20 of BD: the piece, the piece
  taken, the flag; R47 is HASH's by then): a pawn its file and x on a capture (en passant too), =Q on the last row; a
  piece its letter, then :SANDIS: when another piece of its kind could go there legally: from the target along the
  piece's directions (R80-R95, a knight one step), the first piece on each, the square left counted as taken (the
  piece stood there before the move); :SANC: tests the other one's king with the mover back on its square and the
  other's square empty (a pinned piece is left out); then the file, the rank or both. :SQNAME: split into :SQF: and
  :SQR:.
- + and #: :PLAYED: runs :ANYMV: once (R63) before showing the list, :SUFFIX: appends + in check, # with no legal move.
  ANYMV changes R65, so the draw flag is kept in R64; mate and stalemate now come before the draws by repetition and
  material (FIDE; as tools/selfplay47.py's expected_end). A saved game's list (INIT) runs ANYMV only in check, R69 (the
  loop's ply) kept in R62.
- python/chess47ref.py san(p, m), the same rules (also Chess960's castling), checked against python-chess's
  Board.san on 47,199 moves of random games (normal and 960): no difference. tests/test_chess47.py runs the program's
  MAKE + HTEXT + ANYMV + SUFFIX (LBL "TSAN") on every move of 12 positions (disambiguation by file, rank and both, a
  pinned knight, castling, en passant, promotion, check, mate) and the interesting moves of 12 random games, against
  san(); the game's and a saved game's lists too.

## Nov 1, 2026 - v0.3.4: the killer move (branch claude/chess47-killer)

- Tried first: a futility bound on the quiet replies (a reply by x from f gives at least S SC - S value(x, f) -
  max value(x)). In the twin 40 % fewer replies valued, the same answers; in the program 4-5 % slower (the bound once a
  reply, or once a piece kept in BD cells: no register is free): the lazy replies reach the cut early, so only 80 of
  544 DELTA calls were saved. Reverted (branch claude/chess47-speed3, no change).
- The killer move: the reply that cut a root move (:KSET:, from the cut in :QEVAL: / :CEVAL:: the move, its piece and
  what stood on its target, in BD (11, 1-3), cleared by :THINK:) is valued first in the next :REPLY: by :KILLER: when
  it is still a move of the position: its piece on its square, its target as it was, the squares between empty for a
  bishop, rook, queen or a pawn's two steps, never en passant (then it is a pseudo-legal reply, as GEN would make it).
  When it cuts, nothing is generated; else GEN runs as before (the killer valued twice: the least is the same). The
  answer cannot change (the value of a root move is the least over its replies, or below the best when cut).
- The twin: opts 'killer' (in ENGINE), Pos.killer_ok(); with it 13 % fewer replies valued over 44 positions, the same
  moves and values, every killer it took was in GEN's list. The program over 15 positions: 1 407 376 steps -> 914 965
  (65 %), the same move and value each; the three of the profile 253 160 -> 202 617.

## Nov 1, 2026 - v0.4.0: Chess960 (branch claude/chess47-960)

- ÷ (KEY? 55, next to 7 8 9 = 52 53 54: not yet checked on the C47) asks the position's number, three digits (:ASK960:)
  or ÷ again for RAN#; CHN = (n + 1) x 100000 + plies x 100 + level x 10 + side + 2 (an old CHN reads as normal chess);
  BD (11, 7) = n + 1 for the game. INIT: :BACK9: the back ranks by Scharnagl's numbering (python/chess960.py start()),
  :NTH: the k-th free square; :CSQ: the king and the castling rooks from white's back rank into BD (11, 4-6), R24 R25.
- The castling rights: :CRSQ: is now a table (row 23 of BD, 23 x 120: each square's mask, 15 but the kings' and rooks'
  first squares), one lookup and AND for both games (normal chess 1.5 % faster: 914 965 -> 901 370 steps on the 15
  positions of v0.3.4, the same moves).
- Castling: :GCAST: from the king's first square, :CSHRT: / :CLONG: the rook (BD (11, 5 / 6)) and the targets (g f /
  c d), :CAST: the FIDE rule (every square between the king, the rook and their targets empty but those two; the
  king's way and target not attacked, the rook lifted for the test). The move: normal chess the king two squares as
  before (the same lists: the tests), Chess960 the king onto its rook, added as a quiet move (:ADDC:).
- MAKE: a king onto its own rook is Chess960's castling (:C960M:, :KT960: the targets; flag 3); normal castling now
  needs |t - f| + 10 |y| = 2: Chess960's e1-c1 (the rook on c1) moves the king two squares too, and MAKE took it for
  normal castling and moved a1's piece to d1 (the twin's search disagreed in 2 of 24 positions: found and fixed).
  UNMK takes the king and the rook off their targets first (they can stand on each other's squares: king f1, rook
  g1). PLAYED redraws the targets, HTEXT writes O-O / O-O-O for flag 3, BOOK plays nothing in Chess960.
- The twin: chess960.Pos960 makes its castling where GEN does (after the king's own moves, short first) and orders it
  as a quiet move. tests/test_chess47.py: 8 start positions, GEN and THINK in 14 positions with 19 castlings, ÷ 1 2 3
  and castling by the keys, C47 vs C47 (16 plies as the twin), 0 and back, ÷ 9 9 9 refused, ÷ ÷, 7.
  tools/selfplay47.py ... 960: games from random positions checked by python-chess (chess960=True).

## Nov 1, 2026 - v0.5.0: level 3 (60 s), speed-ups, refactoring (branch claude/chess47-level3)

- Level 3 (key 1: 2 -> 1 -> CRAZY -> 3): level 2 first, then :THINK3: the root moves again (level 2's move first),
  each (:ROOT3:) rejected when not legal (:INCHK2:), else a mate (:MATEQ:) or the replies listed (GEN mode 4, ML row
  3) and played (:REPLY3:, the killer first, skipped in the list when it was valued: flag BD (11, 17)); after each reply
  (:R3ONE:, ply 2) S's answers valued as level 2 values the replies (GEN mode 5: :AQEVAL: / :ACEVAL:, RECAP with the
  recapture by the side that did not move: its value with the sign that hurts the mover), the best legal one in R29
  (legality tested only when it is the best so far: MAKE ply 3, INCHK2), the answer killer first (BD (11, 8-10),
  :AKILL:, :KOK: shared with the level-2 killer, :KSET0: with R48 the first column); a reply that takes the king ends
  the line (lost); no legal answer: -29500 in check (mate), 0 (stalemate). The cuts: answers at R29 >= R65, replies at
  R65 <= R61. The time: BD (11, 15) TICKS at the start, (11, 18) the budget (600 tenths, INIT; the tests raise it),
  :TIME3: after each reply and each root move; over: the reply's root move not counted (R65 -30000), then the best of
  the root moves done, or level 2's move. R29 (0 while the C47 thinks) is kept in (11, 14).
- The twin: search(3) = search(2), then search3(first) and answers(); Pos.budget (answers allowed) stands for the
  C47's 60 s in tools/elo47.py (about 0.08 s an answer on the C47: 750). tests/test_chess47.py level3_tests: three
  positions to the end as search(3) (the start 58 s, e5 en passant 118 s, a mate in one either way 37 s), the 60 s
  budget (a legal move within 60 s + level 2), the key.
- Found by tools/elo47.py on the way: level 3 played Nf4xg2 in check (Qxe8 took the king, then Nxe1 took White's:
  even). Now the root move's legality first, the king's capture ends a line, mate below everything legal.
- A bug of the level-3 port, found by the tests (the move lists): the mode-5 test in ADD's capture branch pushed two
  values and the piece taken fell off the 4-level stack (every capture coded 3): DROP DROP after each mode test.
- Speed-ups (15 positions at level 2, the same move in each): ADD reads the target through the index its callers set
  (they all have just read it) and checks the room of the list only where it stores; GEN tests an own piece with X>0?
  (GENSQ rejects the border); DELTA takes from and to from R30 R33 (all its callers have them; R40 is built only in
  ALEGAL and KSET0); VAL inlined in DELTA and MAKE; ATT's diagonals and lines in two loops with the kind as a
  constant. 913 577 -> 839 425 steps (level 3's build; v0.4.0: 901 370).
- Refactoring: GPAWN, GSLIDE, ATTC, ADDC, PSQ, CSQ, FACE, SQXY, C960M and ALEGAL inlined where they were called (one
  caller each; a call after a test became test / IF / ... / ENDIF): 99 -> 89 local labels, 26 steps fewer.
- Tried and not done: the board in local registers (RCL IND: one step a square instead of four). LocR is run already,
  but how local registers behave indirectly and inside subroutines is not checked on the C47: a test for Victor first.

## Nov 3, 2026 - v0.5.1: 7 right after the start, "Not enough memory" (branch claude/chess47-newgame)

- Reported on the forum: 7 (a new game) stopped CHESS47 with "Not enough memory for such a matrix" (on Victor's C47
  "Out of range" at the STOIJ after it), and it would not start again until CLVall. INIT made BD (23 x 120) and GL
  with NEWMAT while the old ones still existed: twice the memory for a moment. A stop (an error, EXIT) left them all,
  so every start failed the same way. The simulator has no memory limit, so the tests never saw it.
- Now: INIT frees an old matrix first (0 STO "BD", "GL", and "GH" for a new game) before NEWMAT. 7 and ÷ set R99 = 1
  (R57 in INIT: R99 survives R-CLR 20.79; the start sets R99 = 0): BD and GL are kept, PSTALL and GLYPHS are not run
  again, and the rows written while playing (2-4, 11, 18-20) are cleared. BD, GL, GH, the registers and the screen
  are as a fresh start's (simulator); a game after 7 plays the same moves as v0.5.0. 7: 69 000 -> 41 000 steps
  (about 12 s -> 7 s).
- "CHESS 47 - SETTING UP ..." at x 106 (was 212): the last dot went to the next row.
