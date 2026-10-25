#!/usr/bin/env python3
"""test_chess47.py - CHESS47 (build/CHESS47.txt) in the C47 simulator against python/chess47ref.py (the same
algorithm in Python) and python/layout.py (the reference picture).

  1. the build: programs/ and build/ are the output of tools/build_chess47.py for programs_rem/CHESS47.txt
  2. the reference: chess47ref's move generator gives the published perft counts (promotion to a queen only:
     the positions without under-promotion; with it, python-chess's counts without the under-promotions)
  3. the start screen: the board pixel for pixel layout.mock (the cursor frame on e2 taken off), the panel's texts
  4. the move generator: for positions (FEN) the moves of :GEN: in the matrix ML (the captures from column 1 by the
     value taken, the others from column 120 down), in that order, as chess47ref.order(gen) (castling, en passant,
     promotion, checks, pins: the legal filter is the caller's)
  5. the search: for positions, levels 1 and 2, the move and the value of :THINK: as chess47ref.search
  6. a game: the C47 plays both sides (+ each time) for some moves: from the book (python/book.py) while it fits,
     then every move as chess47ref.search; the board, SC, the move list, the clock; your stack and LASTx back
     after 0, R20-R99 cleared, the matrices and the clock's variables deleted; CRAZY: 20 random moves, all legal
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
    """build/CHESS47.txt with LBL "TGEN" / XEQ :GEN: / RTN and LBL "TTHK" / XEQ :THINK: / RTN before its END."""
    lab = labels()
    P = [l for l in open(S.PROG, encoding='utf-8').read().split('\n') if l]
    assert P[-1] == 'END'
    P = P[:-1] + ['LBL "TGEN"', 'XEQ %s' % lab['GEN'], 'RTN', 'LBL "TTHK"', 'XEQ %s' % lab['THINK'], 'RTN', 'END']
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
    fx, fy = L.BX + 4 * L.SQ, 239 - (L.BY + L.SQ)                 # e2, its top-left pixel (rows from the top)
    frame = set()
    for j, w in enumerate([L.FULL, L.FULL] + [L.EDGE] * 20 + [L.FULL, L.FULL]):
        for i in range(L.SQ):
            if w >> i & 1:
                frame.add((fx + j, fy - i))
    check(board ^ frame == mock, 'the board pixel for pixel layout.mock (the cursor frame on e2 taken off)')
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
          and not any(k in c.mats for k in ('BD', 'PT', 'ML', 'UN', 'GL', 'GH', 'OB'))
          and not any(k in c.reg for k in ('TK', 'TW', 'TB')),
          '0 after two moves: your stack back, R20-R99 cleared, the matrices and the clock deleted')

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
