#!/usr/bin/env python3
"""test_chess47.py - CHESS47 (build/CHESS47.txt) in the C47 simulator against python/chess47ref.py (the same
algorithm in Python) and python/layout.py (the reference picture).

  1. the build: programs/ and build/ are the output of tools/build_chess47.py for programs_rem/CHESS47.txt
  2. the reference: chess47ref's move generator gives the published perft counts (promotion to a queen only:
     the positions without under-promotion; with it, python-chess's counts without the under-promotions)
  3. the start screen: the board pixel for pixel layout.mock with the cursor's frame on e2, the panel's texts
  4. the move generator: for positions (FEN) the moves of :GEN: in the row 2 of BD (the captures from column 1 by the
     value taken, the others from column 120 down), in that order, as chess47ref.order(gen) (castling, en passant,
     promotion, checks, pins: the legal filter is the caller's)
  5. the search: for positions, levels 1 and 2, the move and the value of :THINK: as chess47ref.search
  6. a game: the C47 plays both sides (+ each time) for some moves: from the book (python/book.py) while it fits,
     then every move as chess47ref.search; the board, SC, the move list, the clock; your stack and LASTx back
     after 0, R20-R99 cleared, BD GL OB deleted, the game kept (CHN GH TW TB); CRAZY: 20 random moves, all legal
  6b. the cursor and the piece picked on a dark square, + (black: the board turned), 9 (the C47 against itself, a
     key stops it), the game kept by 0 and played again at the next start, 7 a new game
  7. your moves: the cursor keys, a legal move played, an illegal one refused (ILLEGAL MOVE), a move into check
     refused (ILLEGAL: CHECK), castling short with the keys

For 4 and 5 a test copy of the program gets global labels before END: "TGEN" (XEQ :GEN:) and "TTHK" (XEQ :THINK:),
run after the start with the position written into BD and the registers.
      python3 tests/test_chess47.py [n]      (n: moves of the game, default 14)"""
import os, re, sys, tempfile
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import c47sim                                                    # noqa: E402
import chess47ref as R                                           # noqa: E402
import chess47sim as S                                           # noqa: E402
import layout as L                                               # noqa: E402
ST, CR = 'ST', 'CR'                                              # the state and the castling masks (matrices since v0.8.0)
FAIL = []


def check(cond, what):
    print('  %s  %s' % ('ok  ' if cond else 'FAIL', what))
    if not cond:
        FAIL.append(what)


def labels():
    txt = open(os.path.join(ROOT, 'listings', 'CHESS47_labels.txt'), encoding='utf-8').read()
    return {m.group(1): m.group(2) for m in re.finditer(r':(\w+):\s+(\d\d)', txt)}


def test_copy():
    """build/CHESS47.txt with LBL "TGEN" / XEQ :NINIT: / XEQ :GEN: / RTN, LBL "TTHK" / XEQ :NINIT: / XEQ :THINK: / RTN
    and LBL "TSAN" (the move R40 played at ply 3, its text as :PLAYED: writes it) before its END (:NINIT: the knight
    words of the position written into BD)."""
    lab = labels()
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l]
    assert P[-1] == 'END'
    P = P[:-1] + ['LBL "TGEN"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['GEN'], 'RTN',
                  'LBL "TTHK"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['THINK'], 'RTN',
                  'LBL "TTH3"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['THINK'], 'XEQ %s' % lab['THINK3'], 'RTN',
                  'LBL "TSAN"', 'XEQ %s' % lab['NINIT'], '3', 'STO 46', 'XEQ %s' % lab['MAKE'], 'XEQ %s' % lab['HTEXT'],
                  'XEQ %s' % lab['ANYMV'], 'STO 63', 'XEQ %s' % lab['SUFFIX'], 'RTN', 'END']
    fn = os.path.join(tempfile.mkdtemp(), 'CHESS47T.txt')
    open(fn, 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    return fn


def setpos(c, p):
    """The position p (chess47ref.Pos) into the simulator: the board BB, the side, en passant, castling, SC, the kings."""
    c.mats['BB'][0] = [D(v) if v != R.OFF else D(8) for v in p.bd[1:]]
    c.reg['20'], c.reg['21'], c.reg['22'] = D(p.sd), D(p.ep), D(p.cr)
    c.reg['23'], c.reg['24'], c.reg['25'] = D(p.sc), D(p.kw), D(p.kb)
    c.cur = 'BB'


FENS = ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',
        'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R b KQkq - 0 1',
        '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1',
        'r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1',
        'r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 b kq - 0 1',
        'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8',
        'rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3',
        'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 3',
        '6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1',
        '4k3/8/8/8/8/8/4q3/4K3 w - - 0 1',
        'k7/8/1Q6/8/8/8/8/7K b - - 0 1']


def frame(f, r):
    """the cursor's frame on the screen square of file f, rank r (0-7 from the bottom left): pixels (x, row from the top)"""
    fx, fy = L.BX + f * L.SQ, 239 - (L.BY + r * L.SQ)
    out = set()
    for j, w in enumerate([L.FULL, L.FULL] + [L.EDGE] * 20 + [L.FULL, L.FULL]):
        for i in range(L.SQ):
            if w >> i & 1:
                out.add((fx + j, fy - i))
    return out


def square(f, r):
    fx, fy = L.BX + f * L.SQ, 239 - (L.BY + r * L.SQ)
    return {(fx + j, fy - i) for j in range(L.SQ) for i in range(L.SQ)}


def onboard(pix):
    return {(x, y) for x, y in pix if L.BX <= x < L.BX + 8 * L.SQ and L.BY <= 239 - y < L.BY + 8 * L.SQ}


def flipped(bd):
    """the board seen from black: the square (r, c) at (11 - r, 9 - c)"""
    out = list(bd)
    for s in range(21, 100):
        r, c = (s - 1) // 10, (s - 1) % 10
        if 2 <= r <= 9 and 1 <= c <= 8:
            out[10 * (11 - r) + (9 - c) + 1] = bd[s]
    return out


def letters_tests():
    print('== the pieces as letters (the key ×, the variable CHF)')
    X = 65
    let = lambda bd, picked=0: {(x, 239 - y) for x, y in L.mock_letters(bd, picked)}
    mock0 = {(x, 239 - y) for x, y in L.mock(R.Pos().bd)}
    shots, c = S.run([X])
    check(c.reg.get('CHF') == 1 and onboard(shots[-1]) == let(R.Pos().bd) | frame(4, 1),
          '×: K Q R B N P white, k q r b n p black, in the firmware\'s font, pixel for pixel layout.mock_letters')
    shots, c = S.run([X, S.LEFT, S.PICK])
    check(onboard(shots[-1]) == let(R.Pos().bd, 35) - frame(3, 1), '× 4 5: d2 picked, its letter white on black (the frame white too)')
    shots, c = S.run([X, S.PICK, S.UP, S.UP, S.PICK])
    check(onboard(shots[-1]) == let(S.board(c)) | frame(4, 3) and S.board(c)[56] == 1 and c.reg.get('CHF') == 1,
          '× e2-e4 and the C47\'s reply: the board in letters as the position')
    shots, c = S.run([X, S.NEW])
    check(c.reg.get('CHF') == 1 and onboard(shots[-1]) == let(R.Pos().bd) | frame(4, 1), '× 7: a new game, the letters kept')
    shots, c = S.run([X, X])
    check(c.reg.get('CHF') == 0 and onboard(shots[-1]) == mock0 | frame(4, 1), '× ×: the pieces drawn again, as the start')
    shots, c = S.run([X, 82])
    check(c.reg.get('CHF') == 1, '× 0: CHF kept at the end (the letters at the next start)')
    shots, c = S.run([82])
    check('CHF' not in c.reg, '0: CHF deleted at the end when the pieces are drawn')


def memory_tests():
    print('== the memory check at the start (MEM)')
    import build_chess47 as B
    k = B.constants()
    need = int(k['MEM']) + int(k['GHM'])                       # BD GL OB, 3 000 to spare, and GH (no saved game)
    shots, c = S.run([], mem=need - 100)
    check(not c.ended and 'BB' not in c.mats, 'MEM %d: "NOT ENOUGH MEMORY", no matrix made, a key awaited' % (need - 100))
    shots, c = S.run([S.PICK], mem=need - 100)
    check(c.ended and not [k for k in tuple(L.MATS) + ('GL', 'OB') if k in c.mats or k in c.reg],
          'a key: the end, BD GL OB deleted')
    shots, c = S.run([], mem=need)
    check(all(k in c.mats for k in L.MATS), 'MEM %d: the game starts (%s + %s for GH needed; v0.6.0: 62 000 + 9 600)'
          % (need, k['MEM'], k['GHM']))


def play_tests():
    print('== the cursor and the piece picked on a dark square, black, the C47 against itself, the game kept')
    mock0 = {(x, 239 - y) for x, y in L.mock(R.Pos().bd)}
    shots, c = S.run([S.LEFT])
    check(onboard(shots[-1]) == mock0 | frame(3, 1), '4: the cursor on d2 (a dark square): a solid frame; e2 as before')
    shots, c = S.run([S.LEFT, S.PICK])
    light = {(x - L.SQ, y) for x, y in mock0 & square(4, 1)}         # the white pawn on a light square (e2), moved to d2
    check(onboard(shots[-1]) == (mock0 - square(3, 1)) | (square(3, 1) - light - frame(3, 1)),
          '5 on d2: the pawn picked shown inverted on a light square (white on black) with the frame in white')
    shots, c = S.run([S.HAND])
    p = R.Pos()
    p.make(int(S.gh(c)[0]), 3)
    mockb = {(x, 239 - y) for x, y in L.mock(flipped(p.bd))}
    check(c.reg.get('27') == -1 and int(c.reg.get('28')) == 86 and onboard(shots[-1]) == mockb | frame(3, 1),
          '+ at the start: you play black, the board turned (black at the bottom), the cursor on e7, after %s'
          % R.mname(int(S.gh(c)[0])))
    shots, c = S.run([S.AUTO] + [None] * 5)
    got = [int(v) for v in S.gh(c) if int(v)]
    check(len(got) == 6 and c.reg.get('27') == 0, '9: the C47 plays both sides (6 plies, no key): %s'
          % ' '.join(R.mname(m) for m in got))
    shots, c = S.run([S.AUTO, None, None, S.PICK])
    got = [int(v) for v in S.gh(c) if int(v)]
    check(len(got) == 3 and c.reg.get('27') == -1 == c.reg.get('20'),
          '9, then a key after 3 plies: you take the side to move (black)')
    shots, c = S.run([S.PICK, S.UP, S.UP, S.PICK, S.END])
    keep = {k: c.reg[k] for k in ('CHN', 'TW', 'TB')}
    gh = c.mats['GH']
    got = [int(v) for v in S.gh_row(gh) if int(v)]
    p, sans = R.Pos(), []
    for m in got:
        sans.append(R.san(p, m))
        p.make(m, 3)
    check(c.ended and keep['CHN'] == 223 and len(got) == 2, '0 after e2-e4 and the reply: CHN 223 (2 plies, level 2, white)')
    shots, c2 = S.run([], regs=keep, mats={'GH': gh})
    hist = [x for x in (c2.reg.get(str(r)) for r in range(73, 80)) if isinstance(x, str)]
    check(S.board(c2)[22:100] == p.bd[22:100] and c2.reg.get('23') == p.sc and c2.reg.get('20') == 1
          and int(c2.reg['96']) == 2 and hist == ['1. e4', '1... ' + sans[1]]
          and onboard(shots[-1]) == {(x, 239 - y) for x, y in L.mock(p.bd)} | frame(4, 1),
          'the next start: the game played again (the board, SC, white to move, move 2, the list, the screen): '
          '%d steps (%.1f s)' % (c2.at_steps[0], S.secs(c2.at_steps[0])))
    old = [[D(m) for m in got] + [D(0)] * (300 - len(got)), [D(0)] * 300]   # a record of v0.6.0: moves, keys in two rows
    shots, c9 = S.run([], regs=keep, mats={'GH': old})
    check(S.board(c9)[22:100] == p.bd[22:100] and S.gh(c9)[:3] == got + [0]
          and all(int(v) // 100000 > 0 for v in c9.mats['GH'][0][:2]),
          'a saved game of v0.6.0 (GH 2 x 300: moves, keys): played again, its record written as key x 100000 + move')
    shots, c3 = S.run([S.PICK, S.UP, S.UP, S.PICK, S.NEW])
    check(S.board(c3)[22:100] == R.Pos().bd[22:100] and not any(int(v) for v in S.gh(c3))
          and onboard(shots[-1]) == mock0 | frame(4, 1), '7: a new game (the start position, the record empty)')
    check(3000 < keep['TW'] < 3100 and 3000 < keep['TB'] < 3100, 'the clock: 5 minutes each (3000 tenths), 10 s a move, '
          'the C47\'s (black) runs too (v0.10.0): W %s, B %s' % (keep['TW'], keep['TB']))
    low = dict(keep, TW=D(5))
    shots, c4 = S.run([None] * 300 + [S.PICK], regs=low, mats={'GH': gh})
    check(c4.reg.get('97') == 1 and c4.reg.get('TW') == 0 and int(S.gh(c4)[2]) == 0,
          'white\'s time runs out while it thinks: WHITE LOST ON TIME, the game over, no move played')
    # the squares drawn after a move: R47 (en passant / castling) must be MAKE's, not the piece count of :HASH:
    lab = labels()
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l][:-1]
    P += ['LBL "TPLY"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['MAKE'], 'XEQ %s' % lab['PLAYED'], 'RTN', 'END']
    fn = os.path.join(tempfile.mkdtemp(), 'CHESS47P.txt')
    open(fn, 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    shots, c5 = S.run([], prog=fn)
    setpos(c5, R.Pos.fen('4k3/8/8/8/8/8/3R3P/4K3 w - - 0 1'))
    c5.reg['40'], c5.reg['46'] = D(39049), D(3)
    c5.run('TPLY', maxsteps=10 ** 8)
    stray = [(x, y) for y, x in c5.pix if L.BX + 8 * L.SQ <= x < 212]
    check(not stray, 'h2-h3 with a rook and a pawn left: nothing drawn off the board (was a rook glyph by h3: %d pixels)'
          % len(stray))
    shots, c7 = S.run([74, S.PICK, S.UP, S.UP, S.PICK, S.UP, S.UP, S.UP, S.PICK, S.DOWN, S.DOWN, S.PICK])
    check(c7.reg.get('27') == 2 and [int(v) for v in S.gh(c7)[:3]] == [36056, 86066, 0]
          and c7.reg['TW'] > 3000 and c7.reg['TB'] > 3000,
          '3: two players: e2-e4 and e7-e5 keyed, no move of the C47, both clocks run (10 s a move)')
    low = dict(keep, TB=D(1))                                    # the C47 (black) with 0.1 s left: it loses on time
    shots, c8 = S.run([S.LEFT, S.PICK, S.UP, S.UP, S.PICK], regs=low, mats={'GH': [list(r) for r in gh]})
    check(c8.reg.get('97') == 1 and int(S.gh(c8)[3]) == 0 and c8.reg.get('TB') == 0 and 'TLV' not in c8.reg
          and c8.reg.get('26') == 2, 'the C47 with 0.1 s left thinks: its clock runs (v0.10.0), BLACK LOST ON TIME, no '
          'move played, its level back (2)')
    # the time-out rule (FIDE 6.9): :TMAT: as python-chess's has_insufficient_material, random positions of few pieces
    import chess, random
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l][:-1]
    P += ['LBL "TTMAT"', 'XEQ %s' % lab['TMAT'], 'RTN', 'END']
    fn = os.path.join(tempfile.mkdtemp(), 'CHESS47M.txt')
    open(fn, 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    shots, c6 = S.run([], prog=fn)
    rnd, diff, n = random.Random(7), [], 0
    for k in range(150):
        b = chess.Board(None)
        sqs = rnd.sample(range(64), 8)
        b.set_piece_at(sqs[0], chess.Piece(chess.KING, True))
        b.set_piece_at(sqs[1], chess.Piece(chess.KING, False))
        for q in sqs[2:2 + rnd.choice([0, 1, 1, 2, 2, 3, 4, 6])]:
            t = rnd.choice('PNNBBBRQ')
            if t == 'P' and chess.square_rank(q) in (0, 7):
                t = 'N'
            b.set_piece_at(q, chess.Piece(chess.Piece.from_symbol(t).piece_type, rnd.random() < 0.5))
        setpos(c6, R.Pos.fen(b.fen()))
        for w in (True, False):
            c6.s = [D(1 if w else -1)] + [D(0)] * 3
            c6.run('TTMAT', maxsteps=10 ** 7)
            n += 1
            if int(c6.s[0]) != int(b.has_insufficient_material(w)):
                diff.append(b.fen())
    check(not diff, 'a time-out: a draw exactly when the opponent cannot mate (python-chess has_insufficient_material, '
          '%d cases)%s' % (n, ' ' + diff[0] if diff else ''))


MINUTES, SECONDS = (5, 3, 5, 10, 15, 90, 90, 0), (10, 2, 3, 5, 10, 30, 30, 0)


def clock_tests():
    """v0.10.0: the time controls (-), the clock off during the game (- -), the C47's clock and its budget."""
    import chess960 as C
    print('== the clock: the time controls (-), CLOCK OFF? (- -), the C47\'s time')
    E4 = [S.PICK, S.UP, S.UP, S.PICK]
    bad = []
    for k in range(1, 9):
        shots, c = S.run([S.CLOCK] * k)
        t = k % 8
        if (c.reg.get('TC'), c.reg.get('TOF'), c.reg.get('TW'), c.reg.get('TB')) != (t, int(t == 7), MINUTES[t] * 600,
                                                                                     MINUTES[t] * 600):
            bad.append((k, c.reg.get('TC'), c.reg.get('TOF'), c.reg.get('TW')))
    check(not bad, '- before the first move, 1 to 8 times: 3+2, 5+3, 10+5, 15+10, 90+30, 90/40+30, NO CLOCK (TOF 1, '
          'the clocks at 0), 5+10 again; both clocks set%s' % ('' if not bad else ' BAD %s' % bad))
    shots, c = S.run([S.CLOCK, S.CLOCK, S.END])
    tc = c.reg.get('TC')
    shots, c0 = S.run([S.CLOCK] * 8 + [S.END])
    shots, c2 = S.run([], regs={k: c.reg[k] for k in ('CHN', 'TC')})
    check(tc == 2 and 'TC' not in c0.reg and c2.reg.get('TC') == 2 and c2.reg.get('TW') == 3000 == c2.reg.get('TB')
          and 'TOF' not in c.reg, 'the control kept between starts (TC 2: 5+3; TC 0 deleted at the end) and set at '
          'the next start: W %s' % c2.reg.get('TW'))
    shots, c = S.run(E4 + [S.CLOCK, S.CLOCK, None])
    tw, tb = c.reg.get('TW'), c.reg.get('TB')
    check(c.reg.get('TOF') == 1 and c.reg.get('TC') == 0 and 0 <= tw < 30 and 0 <= tb < 30,
          'after e4: - and - again: the clock off (TOF 1) for the game, the clocks counting up from 0 (W %s, B %s), '
          'TC kept' % (tw, tb))
    shots, c = S.run(E4 + [S.CLOCK, S.END, S.UP])
    shots, cu = S.run(E4 + [S.UP])
    check(not c.ended and c.reg.get('TOF') == 0 and c.reg.get('28') == cu.reg.get('28') and c.reg['TB'] > 3000,
          'after e4: - and then 0: the clock stays on, the 0 does not end the program, the next key works as before')
    shots, c = S.run(E4 + [S.CLOCK, S.CLOCK, S.END])
    shots, c3 = S.run([S.UP], regs={k: c.reg[k] for k in ('CHN', 'TW', 'TB', 'TOF', 'TC') if k in c.reg},
                      mats={'GH': c.mats['GH']})
    check(c3.reg.get('TOF') == 1 and c3.reg['TW'] >= c.reg['TW'], 'the clock off kept with the saved game (TOF)')
    shots, c = S.run(E4 + [S.CLOCK, S.PICK])
    check(c.reg.get('TC') == 0 and c.reg.get('TOF') == 0, '- after the first move does not change the control')
    # v0.10.1: the firmware's ABS of a long integer 0 tags it positive and SIGN then answers 1 (v0.10.0's arrows did
    # nothing on the C47); c47sim keeps no long integers, so the build must have no ABS right before SIGN
    steps = [ln.strip() for ln in open(S.PROG, encoding='utf-8')]
    absign = [i + 1 for i in range(len(steps) - 1) if steps[i] == 'ABS' and steps[i + 1] == 'SIGN']
    shots, c = S.run([S.CLOCK, S.PICK, S.UP, S.UP, S.LEFT, S.RIGHT, S.RIGHT, S.DOWN])
    check(not absign and c.reg.get('28') == 47,
          'no ABS before SIGN (the firmware: SIGN |0| is 1)%s; the arrows after - and 5: the cursor e2 -> e4 -> d4 -> '
          'f4 -> f3 (%s)' % ('' if not absign else ' BAD at lines %s' % absign, c.reg.get('28')))
    # the C47's budget: Chess960 (no book), the C47 white (+); 3+2: 1800/30 + 20 = 8 s < 15 s: level 1 for the move;
    # 5+10: 3000/30 + 100 = 20 s: level 2; NO CLOCK: level 2
    n, secs = 123, {}
    for tc, depth in ((1, 1), (0, 2), (7, 2)):
        shots, c = S.run([S.HAND], regs={'CHN': D((n + 1) * 100000 + 23), 'TC': D(tc)})
        want = C.Pos960(n).search(depth)[0]
        got = int(S.gh(c)[0])
        used = MINUTES[tc] * 600 + SECONDS[tc] * 10 - int(c.reg['TW']) if tc != 7 else int(c.reg['TW'])
        secs[tc] = used / 10
        check(got == want and c.reg.get('26') == 2 and 'TLV' not in c.reg and (tc != 0 or secs[1] < secs[0] / 2),
              'Chess960 %d, the C47 white at level 2, %s: it thinks at level %d (%s, as chess960.search(%d)), %.1f s; '
              'the level kept (+ turning the board is nobody\'s time)' % (n, {1: '3+2', 0: '5+10', 7: 'NO CLOCK'}[tc], depth,
                                                                         R.mname(got), depth, used / 10))
    # keys pressed while the C47 thinks (typed: the firmware keeps the last one for the next KEY?)
    shots, c = S.run(E4 + [S.END], typed=[S.END])
    shots, c1 = S.run(E4 + [S.UP, S.UP], typed=[S.END])
    shots, cu = S.run(E4 + [S.UP])
    check(c.ended and not c1.ended and c1.reg.get('28') == cu.reg.get('28'),
          '0 pressed while the C47 thinks: END? 0 AGAIN; 0 again ends (the game kept), another key only says no')
    shots, c = S.run(E4 + [S.CLOCK], typed=[S.CLOCK])
    shots, c1 = S.run(E4 + [S.UP], typed=[S.PICK])
    check(c.reg.get('TOF') == 1 and c1.reg.get('28') == cu.reg.get('28') and c1.reg.get('29') == 0,
          '- pressed while it thinks: CLOCK OFF? (- again: off); 5 pressed while it thinks: dropped (nothing picked)')
    n, used = 123, []
    for typed in ([], [S.PICK]):
        shots, c = S.run([S.LEVEL] * 5 + [S.HAND], regs={'CHN': D((n + 1) * 100000 + 23), 'TC': D(7)}, typed=typed)
        used.append((int(c.reg['TW']), int(S.gh(c)[0]), c.reg.get('26')))
    check(used[1][0] < used[0][0] / 3 and used[1][2] == 3 and used[1][1] == C.Pos960(n).search(2)[0],
          'level 3, a key while it thinks: move now (LBL :TIME3:), %.1f s instead of %.1f s, level 2\'s move %s'
          % (used[1][0] / 10, used[0][0] / 10, R.mname(used[1][1])))
    # the budget of a move (LBL :TBUD:) for the controls
    lab = labels()
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l][:-1]
    P += ['LBL "TBUD"', 'XEQ %s' % lab['TBUD'], 'RTN', 'END']
    fn = os.path.join(tempfile.mkdtemp(), 'CHESS47B.txt')
    open(fn, 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    shots, c = S.run([], prog=fn)
    bad = []
    for tc, tw, mv, side, want in ((0, 3000, 1, 1, 200), (1, 1800, 1, 1, 80), (5, 54000, 1, 1, 2100),
                                   (6, 54000, 1, 1, 54000 // 42 + 300), (6, 54000, 40, -1, 13500), (6, 20000, 41, 1, 20000 // 30 + 300),
                                   (4, 400, 30, 1, 100), (7, 999, 5, 1, 10 ** 9)):
        c.reg.update({'TC': D(tc), 'TW': D(tw), 'TB': D(tw), 'TOF': D(int(tc == 7)), '96': D(mv), '20': D(side)})
        c.run('TBUD', maxsteps=10 ** 7)
        got = int(c.s[0])
        if tc == 7:
            ok = got >= 10 ** 9
        else:
            ok = got == want
        if not ok:
            bad.append((tc, tw, mv, got, want))
    check(not bad, 'LBL :TBUD:: the time left / the moves to go (30; 90/40: 43 - the move number) + the seconds a move, '
          'at most a quarter of the time left; 10^9 with the clock off%s' % ('' if not bad else ' BAD %s' % bad))


def main():
    n = int(sys.argv[1]) if sys.argv[1:] else 14
    print('== the build')
    import build_chess47 as B
    st = B.build()
    check(open(os.path.join(ROOT, 'build', 'CHESS47.txt'), encoding='utf-8').read().split('\n')[:-1] == st
          and open(os.path.join(ROOT, 'programs', 'CHESS47.txt'), encoding='utf-8').read().split('\n')[:-1] == st,
          'programs/ and build/CHESS47.txt are the build of programs_rem/CHESS47.txt (%d steps)' % len(st))

    print('== the reference engine: perft (promotion to a queen only)')
    for fen, want in ((FENS[0], (20, 400, 8902)), (FENS[1], (48, 2039, 97862)), (FENS[3], (14, 191, 2812, 43238)),
                      (FENS[4], (6, 228, 8087)), (FENS[6], (41, 1373, 54007))):
        p = R.Pos.fen(fen)
        got = tuple(R.perft(p, d + 1) for d in range(len(want)))
        check(got == want, 'perft %s: %s' % (fen.split()[0][:24], got))

    print('== the start screen')
    shots, c = S.run([])
    pix = shots[-1]
    board = {(x, y) for x, y in pix if L.BX <= x < L.BX + 8 * L.SQ and L.BY <= 239 - y < L.BY + 8 * L.SQ}
    mock = {(x, 239 - y) for x, y in L.mock(R.Pos().bd)}
    check(board == mock | frame(4, 1), 'the board pixel for pixel layout.mock with the cursor\'s frame on e2')
    check(len(c.at_steps) == 1, 'the start: %d steps (%.1f s on the C47 at %.2f ms a step)'
          % (c.at_steps[0], S.secs(c.at_steps[0]), S.STEP_MS))

    print('== the move generator (:GEN:) against chess47ref.gen')
    prog = test_copy()
    for fen in FENS:
        p = R.Pos.fen(fen)
        shots, c = S.run([], prog=prog)
        setpos(c, p)
        c.reg['32'], c.reg['38'], c.reg['39'] = D(p.sd), D(1), D(1)
        c.run('TGEN', maxsteps=10 ** 8)
        nc, nq = int(c.reg['37']), int(c.reg['72'])
        row = c.mats['ML'][0]
        got = [int(row[i]) % 100000 for i in range(nc)] + [int(row[119 - i]) for i in range(nq)]
        k = nc + nq
        p.opts = set(R.ENGINE)
        want = p.order(p.gen(p.sd))
        check(got == want, '%s: %d moves%s' % (fen[:40], k, '' if got == want else ' WANT %d %s' % (
            len(want), [R.mname(m) for m in got if m not in want] + ['-' + R.mname(m) for m in want if m not in got])))

    print('== the move list in standard algebraic notation (:HTEXT:, :SUFFIX:) against chess47ref.san')
    import random
    rnd = random.Random(47)
    cases = []
    for fen in ['4k3/8/8/8/8/8/8/1N1K1N2 w - - 0 1', '1n2k3/8/8/R7/8/8/8/R2K4 w - - 0 1',
                '1k6/8/8/8/7Q/8/8/K3Q2Q w - - 0 1', '4k3/4r3/8/8/8/8/4N3/2N1K3 w - - 0 1',
                '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1', '8/P6k/8/8/8/8/8/K7 w - - 0 1', '1k6/P7/1K6/8/8/8/8/8 w - - 0 1',
                FENS[7], FENS[1], FENS[2], FENS[4], FENS[5]]:
        p = R.Pos.fen(fen)
        cases += [(fen, m) for m in p.legal()]
    for g in range(12):                                  # positions of random games: the interesting moves
        p = R.Pos()
        for k in range(rnd.randrange(10, 70)):
            ms = p.legal()
            if not ms:
                break
            p.make(rnd.choice(ms), 3)
        ms = p.legal()
        fen = p
        for m in ms:
            t = R.san(p, m)
            if any(ch in t for ch in '+#=O') or (t[0] in 'NBRQ' and len(t.rstrip('+#').replace('x', '')) > 3) \
                    or rnd.random() < 0.15:
                cases.append((p, m))
    bad, kinds = [], set()
    for fen, m in cases:
        p = R.Pos.fen(fen) if isinstance(fen, str) else fen
        want = R.san(p, m)
        shots, c = S.run([], prog=prog)
        setpos(c, p)
        c.reg['40'], c.reg['96'] = D(m), D(1)
        c.run('TSAN', maxsteps=10 ** 8)
        got = c.reg.get('79', '')
        got = got.split(' ', 1)[1] if isinstance(got, str) and ' ' in got else got
        if got != want:
            bad.append('%s %s %s' % (want, got, p.bd[22:100]))
        kinds |= {k for k, ok in (('capture', 'x' in want), ('check', '+' in want), ('mate', '#' in want),
                                  ('castling', 'O-O' in want), ('promotion', '=Q' in want),
                                  ('file or rank', want[0] in 'NBRQ' and len(want.rstrip('+#').replace('x', '')) == 4),
                                  ('both', want[0] in 'NBRQ' and len(want.rstrip('+#').replace('x', '')) == 5)) if ok}
    check(not bad, '%d moves as python/chess47ref.san (%s)%s' % (len(cases), ', '.join(sorted(kinds)),
          '' if not bad else ' FIRST WANT/GOT %s' % bad[0]))

    print('== the search (:THINK:) against chess47ref.search')
    for fen in FENS[:3] + FENS[7:]:
        for level in (1, 2):
            p = R.Pos.fen(fen)
            shots, c = S.run([], prog=prog)
            setpos(c, p)
            c.reg['26'] = D(level)
            c.steps = 0
            c.run('TTHK', maxsteps=10 ** 9)
            m, v, nodes = p.search(level)
            got = (int(c.reg['62']), int(c.reg['61']))
            check(got == (m, v), '%s level %d: %s %d (%.0f s on the C47)%s' % (
                fen[:36], level, R.mname(got[0]) if got[0] else '-', got[1], S.secs(c.steps),
                '' if got == (m, v) else ' WANT %s %d' % (R.mname(m) if m else '-', v)))

    print('== a king never moves next to the other king (v0.7.1: no recapture bonus when the reply takes the king)')
    import chess
    for fen in ('2n5/3B4/2K5/k1N5/8/8/8/Q7 b - - 0 1', '8/4B3/8/8/7Q/4P1K1/5q2/4k3 w - - 0 1',
                '1R6/3b4/6N1/5k1K/8/8/8/7B b - - 0 1'):
        p = R.Pos.fen(fen)
        shots, c = S.run([], prog=prog)
        setpos(c, p)
        c.reg['26'] = D(2)
        c.run('TTHK', maxsteps=10 ** 9)
        m = int(c.reg['62'])
        mv = chess.Move(chess.square((m // 1000 - 1) % 10 - 1, (m // 1000 - 1) // 10 - 2),
                        chess.square((m % 1000 - 1) % 10 - 1, (m % 1000 - 1) // 10 - 2))
        check(mv in chess.Board(fen).legal_moves and (m, int(c.reg['61'])) == p.search(2)[:2],
              '%s: %s, legal, as the twin (v0.7.0 played a king move next to the other king)' % (fen[:30], R.mname(m)))

    print('== a game: the C47 plays both sides (%d moves; the book first, then the search)' % n)
    import book
    shots, c = S.run([S.HAND] * n)
    got = [int(v) for v in S.gh(c) if int(v)]
    p = R.Pos()
    good, hist_ok, texts, num, inbook = True, [], [], 1, 0
    for k, m in enumerate(got):
        cands = book.candidates(got[:k]) if k < 10 else []
        if cands:
            good &= m in cands; inbook += 1
        else:
            want, v, nodes = p.search(2)
            good &= m == want
        texts.append(('%d. ' % num if k % 2 == 0 else '%d... ' % num) + R.san(p, m))
        p.make(m, 3)
        num += k % 2
    check(len(got) == n and good, '%d moves, %d from the book (one of its lines that fit), the others as chess47ref.search: %s'
          % (len(got), inbook, ' '.join(texts)))
    hist = [x for x in (c.reg.get(str(r)) for r in range(73, 80)) if isinstance(x, str)]
    check(hist == texts[-7:], 'the move list (R73-R79) as the moves')
    check(S.board(c)[22:100] == p.bd[22:100] and c.reg.get('23') == p.sc, 'the board and SC after them as chess47ref')
    times = [S.secs(b - a) for a, b in zip(c.at_steps, c.at_steps[1:])]
    check(True, 'the C47 a move (with its drawing): %s s' % ' '.join('%.0f' % t for t in times))
    check(isinstance(c.reg.get('TW'), D) and c.reg['TW'] > 0 and c.reg['TB'] > 0, 'the clock: white %s, black %s tenths'
          % (c.reg.get('TW'), c.reg.get('TB')))
    shots, c = S.run([S.HAND, S.HAND, S.END], stack=(11, 12, 13, 14))
    check(c.ended and c.s == [D(11), D(12), D(13), D(14)] and all(c.reg.get(str(r), D(0)) == 0 for r in range(20, 100))
          and not any(k in c.mats for k in tuple(L.MATS) + ('GL', 'OB')) and 'GH' in c.mats
          and not any(k in c.reg for k in ('TK', 'NW', 'NB')) and c.reg.get('CHN') == 223,
          '0 after two moves: your stack back, R20-R99 cleared, BD GL OB TK NW NB deleted; the game kept: CHN %s, GH TW TB'
          % c.reg.get('CHN'))
    import c47sim
    for mode in ('2COMPL', 'UNSIGN'):                        # your integer mode back (CHESS47 runs in UNSIGN)
        cc = c47sim.load([S.PROG]); cc.s = [D(1)] * 4; cc.pix = []; cc.keys = [S.HAND, S.END]; cc.steps = 0
        cc.frames = []; cc.signmode = mode; S.typeahead(cc)
        cc.run('CHESS47', maxsteps=10 ** 9)
        check(cc.signmode == mode, 'started in %s, ended in %s (the sim refuses SINT out of range, as the C47)'
              % (mode, cc.signmode))

    play_tests()
    clock_tests()
    letters_tests()
    memory_tests()

    print('== CRAZY (level 0): random legal moves')
    import chess
    shots, c = S.run([S.LEVEL, S.LEVEL] + [S.HAND] * 20)
    got = [int(v) for v in S.gh(c) if int(v)]
    b, ok = chess.Board(), True
    for m in got:
        f, t = m // 1000, m % 1000
        mv = chess.Move(chess.square((f - 1) % 10 - 1, (f - 1) // 10 - 2), chess.square((t - 1) % 10 - 1, (t - 1) // 10 - 2))
        if b.piece_at(mv.from_square).piece_type == chess.PAWN and chess.square_rank(mv.to_square) in (0, 7):
            mv.promotion = chess.QUEEN
        ok &= mv in b.legal_moves
        if not ok:
            break
        b.push(mv)
    check(ok and len(got) == 20 and c.reg.get('26') == 0, '20 moves at level 0, all legal: %s' % chess.Board().variation_san(b.move_stack))

    print('== your moves with the keys')
    # e2-e4 (the cursor starts on e2): 5, 8 8, 5; then the C47's reply
    shots, c = S.run([S.PICK, S.UP, S.UP, S.PICK])
    reply = int(S.gh(c)[1])
    p = R.Pos(); p.make(36056, 3); p.make(reply, 3)
    check(int(S.gh(c)[0]) == 36056 and reply in book.candidates([36056]) and S.board(c)[22:100] == p.bd[22:100],
          'e2-e4 with 5 8 8 5, then the C47 from its book: %s, the board' % R.mname(reply))
    # an illegal move: e2-e5 (5 8 8 8 5)
    shots, c = S.run([S.PICK, S.UP, S.UP, S.UP, S.PICK])
    check(c.reg.get('20') == 1 and S.board(c)[36] == 1, 'e2-e5 refused: the pawn stays, white to move')
    chess960_tests(prog)
    level3_tests(prog)
    kirk_tests()
    variant_tests()
    print('\n%s' % ('ALL OK' if not FAIL else '%d FAILED' % len(FAIL)))
    return 1 if FAIL else 0


def kirk_tests():
    """÷ 1701, the Easter egg as chess47.pg5's: the C47 keeps its king and pawns (pg5's FENs), no book, KIRK WINS."""
    print('== Kirk (÷ 1 7 0 1): the Kobayashi Maru')
    K = [55, 72, 52, 82, 72]                                     # ÷ 1 7 0 1
    W = '4k3/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1'       # you white: black keeps its king and pawns
    B = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/4K3 w kq - 0 1'       # you black: white the same
    shots, c = S.run(K)
    p = R.Pos.fen(W)
    check(S.board(c)[22:100] == p.bd[22:100] and c.reg.get('22') == p.cr and c.reg.get('23') == p.sc
          and int(c.reg['CHN']) // 100000 == 1702 and int(c.mats['ST'][0][6]) == 0,
          '÷ 1701: %s, castling %d, SC %d (as chess47ref), CHN position 1701, not Chess960' % (W.split()[0], p.cr, p.sc))
    shots, c = S.run(K + [S.PICK, S.UP, S.UP, S.PICK])
    got = [int(x) for x in S.gh(c) if int(x)]
    q = R.Pos.fen(W)
    q.make(got[0], 3); q.undo.pop(3)
    want, v, n = q.search(2)
    q.make(got[1], 3); q.undo.pop(3)
    check(len(got) == 2 and got[1] == want and S.board(c)[22:100] == q.bd[22:100] and c.reg.get('23') == q.sc,
          'e2-e4: the C47 answers %s as chess47ref.search (no book: it has no knights)' % R.mname(want))
    shots, c = S.run([S.HAND] + K)
    p = R.Pos.fen(B)
    want, v, n = p.search(2)
    got = [int(x) for x in S.gh(c) if int(x)]
    p.make(want, 3); p.undo.pop(3)
    check(got == [want] and S.board(c)[22:100] == p.bd[22:100] and c.reg.get('22') == p.cr and c.reg.get('23') == p.sc,
          '+ ÷ 1701: you black, white keeps its king and pawns (%s) and opens %s' % (B.split()[0], R.mname(want)))
    shots, c = S.run(K + [S.PICK, S.UP, S.UP, S.PICK, S.END])
    keep, gh = {k: c.reg[k] for k in ('CHN', 'TW', 'TB')}, c.mats['GH']
    shots, c2 = S.run([], regs=keep, mats={'GH': gh})
    q = R.Pos.fen(W)
    for m in [int(x) for x in S.gh_row(gh) if int(x)]:
        q.make(m, 3); q.undo.pop(3)
    check(S.board(c2)[22:100] == q.bd[22:100] and c2.reg.get('23') == q.sc and c2.reg.get('22') == q.cr,
          '0 and the next start: Kirk\'s game goes on (CHN %s)' % keep['CHN'])
    shots, c = S.run([74] + K)
    check(c.reg.get('27') == 2 and S.board(c)[22:30] == R.Pos.fen(W).bd[22:30] and S.board(c)[92:100] ==
          R.Pos.fen(W).bd[92:100], '3 ÷ 1701 (two players): black keeps its king and pawns, as chess47.pg5')
    keys, cur = [74] + K, (4, 1)                                 # two players; the cursor on e2
    for mv in ('e2e3', 'e8f8', 'd1g4', 'd7d6', 'g4c8'):          # the shortest mate (python-chess)
        for sq in (mv[:2], mv[2:]):
            f, r = ord(sq[0]) - 97, int(sq[1]) - 1
            keys += [S.RIGHT if f > cur[0] else S.LEFT] * abs(f - cur[0]) + [S.UP if r > cur[1] else S.DOWN] * abs(r - cur[1])
            keys.append(S.PICK)
            cur = (f, r)
    texts, atext = [], c47sim.Calc.atext                        # the texts written (ATEXT) recorded
    c47sim.Calc.atext = lambda self, t, *a, **k: (texts.append(t), atext(self, t, *a, **k))[1]
    try:
        shots, c = S.run(keys)
    finally:
        c47sim.Calc.atext = atext
    hist = [x for x in (c.reg.get(str(r)) for r in range(73, 80)) if isinstance(x, str)]
    check(hist[-1:] == ['3. Qc8#'] and c.reg.get('97') == 1 and any('KIRK WINS' in str(t) for t in texts)
          and not any('CHECKMATE' in str(t) for t in texts),
          'two players: 1. e3 Kf8 2. Qg4 d6 3. Qc8#: the game over, KIRK WINS (%s)' % ' '.join(hist))
    shots, c = S.run([S.NEW] + K + [S.NEW])
    check(S.board(c)[22:100] == R.Pos().bd[22:100] and int(c.reg['CHN']) // 100000 == 0, '7 after Kirk: normal chess again')


def variant_tests():
    """v0.8.1: the two builds, build/draw/ (the pieces drawn, GL) and build/text/ (letters only, no GL, no key ×):
    the same game, the start's memory."""
    print('== the two builds: build/draw/ and build/text/')
    import build_chess47 as B
    games = {}
    for name in B.VARIANTS:
        shots, c = S.run([S.HAND] * 4, prog=os.path.join(ROOT, 'build', name, 'CHESS47.txt'))
        games[name] = S.gh(c)[:4]
        check(('GL' in c.mats) == (name == 'draw') and int(c.reg.get('CHF', 0)) == (name == 'text'),
              '%s: GL %s, CHF %s, the C47 played %s' % (name, 'made' if 'GL' in c.mats else 'none',
                                                         c.reg.get('CHF'), ' '.join(R.mname(m) for m in games[name])))
    check(games['draw'] == games['text'] and all(games['draw']), 'the same moves in both')


def level3_tests(prog):
    """Level 3 (LBL :THINK3:) against chess47ref.search(3): to the end (the budget raised), then with the C47's 60 s."""
    import copy
    print('== level 3 (:THINK3:) against chess47ref.search(3)')
    for f in (FENS[0], FENS[7], 'r1b1kb1r/2p1pppp/2Q5/p3N3/2PPpn2/P6P/1P3PP1/RN2K2R b KQkq - 0 12'):
        p = R.Pos.fen(f)
        shots, c = S.run([], prog=prog)
        setpos(c, p)
        c.reg['26'] = D(3)
        c.mats['ST'][0][17] = D(10 ** 9)                      # no time limit
        c.steps = 0
        c.run('TTH3', maxsteps=10 ** 10)
        m, v, n = copy.deepcopy(p).search(3)
        got = (int(c.reg['62']), int(c.reg['61']))
        check(got == (m, v), '%s: %s %d (%.0f s on the C47 to the end)%s' % (
            f[:40], R.mname(got[0]), got[1], S.secs(c.steps), '' if got == (m, v) else ' WANT %s %d' % (R.mname(m), v)))
    p = R.Pos.fen(FENS[1])
    shots, c = S.run([], prog=prog)
    setpos(c, p)
    c.reg['26'] = D(3)
    c.steps = 0
    c.run('TTH3', maxsteps=10 ** 10)
    secs = S.secs(c.steps)
    check(int(c.reg['62']) in p.legal() and secs < 60 + 25 and c.reg.get('29') == 0,
          '%s with the 60 s budget: %s, %.0f s in all (level 2 first; the time over: the best found so far), R29 '
          'back to 0' % (FENS[1][:30], R.mname(int(c.reg['62'])), secs))
    shots, c = S.run([S.LEVEL, S.LEVEL, S.LEVEL])
    check(c.reg.get('26') == 5 and int(c.mats['ST'][0][17]) == 5400,
          'the key 1 three times: level 2 -> 1 -> CRAZY -> 5 (v0.8.1: level 3 with 9 min, 5400 tenths)')
    shots, c = S.run([S.LEVEL] * 5)
    check(c.reg.get('26') == 3 and int(c.mats['ST'][0][17]) == 600,
          'five times: -> 4 -> 3 (60 s, 600 tenths); six: back to 2')


def setpos960(c, p, n):
    """A Chess960 position (chess960.Pos960 of the start n) into the simulator: setpos, then ST columns 4-7 (the king's
    and the castling rooks' first squares, n + 1) and the masks of the castling rights (CR), as INIT's LBL :CSQ:."""
    setpos(c, p)
    m = {ST: c.mats['ST'][0], CR: c.mats['CR'][0]}
    m[ST][3], m[ST][4], m[ST][5], m[ST][6] = D(p.home[1]), D(p.rook[1][1]), D(p.rook[1][2]), D(n + 1)
    for s in range(22, 100):
        m[CR][s - 1] = D(15)
    for s, v in ((p.home[1], 12), (p.rook[1][1], 14), (p.rook[1][2], 13), (p.home[-1], 3), (p.rook[-1][4], 11),
                 (p.rook[-1][8], 7)):
        m[CR][s - 1] = D(v)


def chess960_tests(prog):
    """Chess960 (v0.4.0) against python/chess960.py (its twin; checked against python-chess by tests/test_960.py)."""
    import copy, random
    import chess960 as C
    DIV = 55
    print('== Chess960: the start positions (CHN (n + 1) x 100000 + ...)')
    bad = []
    for n in (518, 0, 959, 123, 66, 300, 440, 777):
        shots, c = S.run([], regs={'CHN': D((n + 1) * 100000 + 23)})
        p, m = C.Pos960(n), {ST: c.mats['ST'][0], CR: c.mats['CR'][0]}
        masks = {s: int(m[CR][s - 1]) for s in range(22, 100) if int(m[CR][s - 1]) != 15}
        want = {p.home[1]: 12, p.rook[1][1]: 14, p.rook[1][2]: 13, p.home[-1]: 3, p.rook[-1][4]: 11, p.rook[-1][8]: 7}
        if not (S.board(c)[22:100] == p.bd[22:100] and c.reg['24'] == p.kw and c.reg['25'] == p.kb and masks == want
                and [int(m[ST][k]) for k in (3, 4, 5, 6)] == [p.home[1], p.rook[1][1], p.rook[1][2], n + 1]):
            bad.append(n)
    check(not bad, 'the back ranks of 8 positions (518 normal chess, 0, 959 ...) as chess960.start, the kings, the castling '
          'rooks, the masks of the castling rights%s' % ('' if not bad else ' BAD %s' % bad))
    print('== Chess960: castling (:GCAST:, :CAST:) and the search (:THINK:) against chess960.Pos960')
    rnd = random.Random(47)
    gbad, tbad, ncast, npos = [], [], 0, 0
    while npos < 14:
        n = rnd.randrange(960)
        p = C.Pos960(n)
        for s in list(range(22, 30)) + list(range(92, 100)):     # the back ranks cleared but kings and rooks
            if abs(p.bd[s]) not in (4, 6) and rnd.random() < 0.8:
                p.bd[s] = 0
        for s in list(range(32, 40)) + list(range(82, 90)):      # some pawns off: attacks on the king's way
            if rnd.random() < 0.3:
                p.bd[s] = 0
        if rnd.random() < 0.5:
            p.sd = -1
        p.sc = sum(R.value(p.bd[s], s) for s in range(22, 100) if p.bd[s] != R.OFF)
        if p.attacked(p.king(-p.sd), p.sd) or not p.legal():
            continue
        npos += 1
        shots, c = S.run([], prog=prog)
        setpos960(c, p, n)
        c.reg['32'], c.reg['38'], c.reg['39'] = D(p.sd), D(1), D(1)
        c.run('TGEN', maxsteps=10 ** 8)
        nc, nq = int(c.reg['37']), int(c.reg['72'])
        row = c.mats['ML'][0]
        got = [int(row[i]) % 100000 for i in range(nc)] + [int(row[119 - i]) for i in range(nq)]
        p.opts = set(R.ENGINE)
        want = p.order(p.gen(p.sd))
        ncast += sum(p.castle_move(m) for m in want)
        if got != want:
            gbad.append(p.fen_board())
        q = copy.deepcopy(p)
        shots, c = S.run([], prog=prog)
        setpos960(c, p, n)
        c.reg['26'] = D(2)
        c.run('TTHK', maxsteps=10 ** 9)
        m, v, nodes = q.search(2)
        if (int(c.reg['62']), int(c.reg['61'])) != (m, v):
            tbad.append(p.fen_board())
    check(not gbad and ncast >= 15, '%d positions: the moves in the same order, %d castlings among them (onto the rook)%s'
          % (npos, ncast, '' if not gbad else ' DIFFER %s' % gbad[0]))
    check(not tbad, 'the same move and value at level 2 (castling among the root moves; one of them moves the king '
          'two squares, e1-c1: not the normal castling rook move)%s' % ('' if not tbad else ' DIFFER %s' % tbad[0]))
    print('== Chess960 with the keys: ÷ and the number, castling (king, then its rook), C47 vs C47, 0 and back')
    shots, c = S.run([DIV, 72, 73, 74, S.DOWN, S.RIGHT, S.PICK, S.RIGHT, S.PICK])
    b = S.board(c)
    check(b[28] == 6 and b[27] == 4 and c.reg.get('78') == '1. O-O' and int(c.mats['ST'][0][6]) == 124,
          '÷ 1 2 3: No 123 (NQRNBKRB); 2 6 5 6 5: the king f1 onto its rook g1: O-O, the king on g1, the rook on f1')
    n = 16
    shots, c = S.run([DIV, 72, 73, 74] + [S.HAND] * n)
    got = [int(v) for v in S.gh(c) if int(v)]
    p, ok, texts = C.Pos960(123), True, []
    for m in got:
        want, v, nodes = p.search(2)
        ok &= m == want
        texts.append(R.san(p, m))
        p.make(m, 3)
        p.undo.pop(3)
    check(ok and len(got) == n and S.board(c)[22:100] == p.bd[22:100] and c.reg.get('23') == p.sc,
          'C47 vs C47 in No 123: %d plies as chess960.Pos960.search (no book): %s' % (len(got), ' '.join(texts)))
    shots, c = S.run([DIV, 72, 73, 74, S.HAND, S.HAND, S.HAND, S.END])
    keep, gh = {k: c.reg[k] for k in ('CHN', 'TW', 'TB')}, c.mats['GH']
    got = [int(v) for v in S.gh_row(gh) if int(v)]
    shots, c2 = S.run([], regs=keep, mats={'GH': gh})
    p = C.Pos960(123)
    for m in got:
        p.make(m, 3)
    check(keep['CHN'] == 12400321 and S.board(c2)[22:100] == p.bd[22:100] and int(c2.mats['ST'][0][6]) == 124,
          '0 after 3 plies: CHN %s (No 123, 3 plies, level 2, white); the next start goes on in No 123' % keep['CHN'])
    shots, c = S.run([DIV, 54, 54, 54])
    check(int(c.mats['ST'][0][6]) == 0 and S.board(c)[22:30] == R.Pos().bd[22:30], '÷ 9 9 9: refused (960: 000 TO 959)')
    shots, c = S.run([DIV, DIV])
    check(int(c.mats['ST'][0][6]) > 0, '÷ ÷: a random position (No %d)' % (int(c.mats['ST'][0][6]) - 1))
    shots, c = S.run([DIV, 72, 73, 74, S.NEW])
    check(int(c.mats['ST'][0][6]) == 0 and S.board(c)[22:30] == R.Pos().bd[22:30], '7: a new game of normal chess')


if __name__ == '__main__':
    sys.exit(main())
