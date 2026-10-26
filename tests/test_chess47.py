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
FAIL = []


def check(cond, what):
    print('  %s  %s' % ('ok  ' if cond else 'FAIL', what))
    if not cond:
        FAIL.append(what)


def labels():
    txt = open(os.path.join(ROOT, 'listings', 'CHESS47_labels.txt'), encoding='utf-8').read()
    return {m.group(1): m.group(2) for m in re.finditer(r':(\w+):\s+(\d\d)', txt)}


def test_copy():
    """build/CHESS47.txt with LBL "TGEN" / XEQ :NINIT: / XEQ :GEN: / RTN and LBL "TTHK" / XEQ :NINIT: / XEQ :THINK: / RTN
    before its END (:NINIT: the knight words of the position written into BD)."""
    lab = labels()
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l]
    assert P[-1] == 'END'
    P = P[:-1] + ['LBL "TGEN"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['GEN'], 'RTN',
                  'LBL "TTHK"', 'XEQ %s' % lab['NINIT'], 'XEQ %s' % lab['THINK'], 'RTN', 'END']
    fn = os.path.join(tempfile.mkdtemp(), 'CHESS47T.txt')
    open(fn, 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    return fn


def setpos(c, p):
    """The position p (chess47ref.Pos) into the simulator: BD, the side, en passant, castling, SC, the kings."""
    c.mats['BD'][0] = [D(v) if v != R.OFF else D(8) for v in p.bd[1:]]
    c.reg['20'], c.reg['21'], c.reg['22'] = D(p.sd), D(p.ep), D(p.cr)
    c.reg['23'], c.reg['24'], c.reg['25'] = D(p.sc), D(p.kw), D(p.kb)
    c.cur = 'BD'


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
    p.make(int(c.mats['GH'][0][0]), 3)
    mockb = {(x, 239 - y) for x, y in L.mock(flipped(p.bd))}
    check(c.reg.get('27') == -1 and int(c.reg.get('28')) == 86 and onboard(shots[-1]) == mockb | frame(3, 1),
          '+ at the start: you play black, the board turned (black at the bottom), the cursor on e7, after %s'
          % R.mname(int(c.mats['GH'][0][0])))
    shots, c = S.run([S.AUTO] + [None] * 5)
    got = [int(v) for v in c.mats['GH'][0] if int(v)]
    check(len(got) == 6 and c.reg.get('27') == 0, '9: the C47 plays both sides (6 plies, no key): %s'
          % ' '.join(R.mname(m) for m in got))
    shots, c = S.run([S.AUTO, None, None, S.PICK])
    got = [int(v) for v in c.mats['GH'][0] if int(v)]
    check(len(got) == 3 and c.reg.get('27') == -1 == c.reg.get('20'),
          '9, then a key after 3 plies: you take the side to move (black)')
    shots, c = S.run([S.PICK, S.UP, S.UP, S.PICK, S.END])
    keep = {k: c.reg[k] for k in ('CHN', 'TW', 'TB')}
    gh = c.mats['GH']
    got = [int(v) for v in gh[0] if int(v)]
    p = R.Pos()
    for m in got:
        p.make(m, 3)
    check(c.ended and keep['CHN'] == 223 and len(got) == 2, '0 after e2-e4 and the reply: CHN 223 (2 plies, level 2, white)')
    shots, c2 = S.run([], regs=keep, mats={'GH': gh})
    hist = [x for x in (c2.reg.get(str(r)) for r in range(73, 80)) if isinstance(x, str)]
    check(S.board(c2)[22:100] == p.bd[22:100] and c2.reg.get('23') == p.sc and c2.reg.get('20') == 1
          and int(c2.reg['96']) == 2 and hist == ['1. e2e4', '1... ' + R.mname(got[1])]
          and onboard(shots[-1]) == {(x, 239 - y) for x, y in L.mock(p.bd)} | frame(4, 1),
          'the next start: the game played again (the board, SC, white to move, move 2, the list, the screen): '
          '%d steps (%.1f s)' % (c2.at_steps[0], S.secs(c2.at_steps[0])))
    shots, c3 = S.run([S.PICK, S.UP, S.UP, S.PICK, S.NEW])
    check(S.board(c3)[22:100] == R.Pos().bd[22:100] and not any(int(v) for v in c3.mats['GH'][0])
          and onboard(shots[-1]) == mock0 | frame(4, 1), '7: a new game (the start position, the record empty)')
    check(keep['TW'] > 3000 and keep['TB'] > 3000, 'the clock: 5 minutes each (3000 tenths) + 10 s a move: W %s, B %s'
          % (keep['TW'], keep['TB']))
    low = dict(keep, TW=D(5))
    shots, c4 = S.run([None] * 300 + [S.PICK], regs=low, mats={'GH': gh})
    check(c4.reg.get('97') == 1 and c4.reg.get('TW') == 0 and int(c4.mats['GH'][0][2]) == 0,
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
        c.reg['32'], c.reg['38'], c.reg['39'] = D(p.sd), D(2), D(1)
        c.run('TGEN', maxsteps=10 ** 8)
        nc, nq = int(c.reg['37']), int(c.reg['72'])
        row = c.mats['BD'][1]
        got = [int(row[i]) % 100000 for i in range(nc)] + [int(row[119 - i]) for i in range(nq)]
        k = nc + nq
        p.opts = set(R.ENGINE)
        want = p.order(p.gen(p.sd))
        check(got == want, '%s: %d moves%s' % (fen[:40], k, '' if got == want else ' WANT %d %s' % (
            len(want), [R.mname(m) for m in got if m not in want] + ['-' + R.mname(m) for m in want if m not in got])))

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

    print('== a game: the C47 plays both sides (%d moves; the book first, then the search)' % n)
    import book
    shots, c = S.run([S.HAND] * n)
    got = [int(v) for v in c.mats['GH'][0] if int(v)]
    p = R.Pos()
    good, hist_ok, texts, num, inbook = True, [], [], 1, 0
    for k, m in enumerate(got):
        cands = book.candidates(got[:k]) if k < 10 else []
        if cands:
            good &= m in cands; inbook += 1
        else:
            want, v, nodes = p.search(2)
            good &= m == want
        p.make(m, 3)
        texts.append(('%d. ' % num if k % 2 == 0 else '%d... ' % num) + R.mname(m))
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
          and not any(k in c.mats for k in ('BD', 'GL', 'OB')) and 'GH' in c.mats
          and not any(k in c.reg for k in ('TK', 'NW', 'NB')) and c.reg.get('CHN') == 223,
          '0 after two moves: your stack back, R20-R99 cleared, BD GL OB TK NW NB deleted; the game kept: CHN %s, GH TW TB'
          % c.reg.get('CHN'))
    import c47sim
    for mode in ('2COMPL', 'UNSIGN'):                        # your integer mode back (CHESS47 runs in UNSIGN)
        cc = c47sim.load([S.PROG]); cc.s = [D(1)] * 4; cc.pix = []; cc.keys = [S.HAND, S.END]; cc.steps = 0
        cc.frames = []; cc.signmode = mode
        cc.run('CHESS47', maxsteps=10 ** 9)
        check(cc.signmode == mode, 'started in %s, ended in %s (the sim refuses SINT out of range, as the C47)'
              % (mode, cc.signmode))

    play_tests()

    print('== CRAZY (level 0): random legal moves')
    import chess
    shots, c = S.run([S.LEVEL, S.LEVEL] + [S.HAND] * 20)
    got = [int(v) for v in c.mats['GH'][0] if int(v)]
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
    reply = int(c.mats['GH'][0][1])
    p = R.Pos(); p.make(36056, 3); p.make(reply, 3)
    check(int(c.mats['GH'][0][0]) == 36056 and reply in book.candidates([36056]) and S.board(c)[22:100] == p.bd[22:100],
          'e2-e4 with 5 8 8 5, then the C47 from its book: %s, the board' % R.mname(reply))
    # an illegal move: e2-e5 (5 8 8 8 5)
    shots, c = S.run([S.PICK, S.UP, S.UP, S.UP, S.PICK])
    check(c.reg.get('20') == 1 and S.board(c)[36] == 1, 'e2-e5 refused: the pawn stays, white to move')
    print('\n%s' % ('ALL OK' if not FAIL else '%d FAILED' % len(FAIL)))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
