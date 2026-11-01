"""test_960.py - python/chess960.py against python-chess (pip install chess): the 960 start positions, the move
counts (perft 3) of some, and the legal moves (castling included) at every ply of random games; then games of the
engine (level 2) checked move by move. python3 tests/test_960.py"""
import os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import chess
import chess960 as C

FAIL = []


def check(ok, text):
    print('  %s  %s' % ('ok  ' if ok else 'FAIL', text))
    if not ok:
        FAIL.append(text)


def sq(s):
    return chess.square((s - 1) % 10 - 1, (s - 1) // 10 - 2)


def uci(p, m):
    """Our move -> python-chess's (Chess960: castling is king -> rook; a promotion a queen)."""
    f, t = m // 1000, m % 1000
    promo = chess.QUEEN if abs(p.bd[f]) == 1 and (t > 90 or t < 30) else None
    return chess.Move(sq(f), sq(t), promotion=promo)


def same_board(p, b):
    return p.fen_board() == b.board_fen()


print('== the start positions')
check(all(C.letters(n) == chess.Board.from_chess960_pos(n).board_fen().split('/')[-1] for n in range(960)),
      'the 960 back ranks as python-chess (518 = %s)' % C.letters(518))


def cperft(b, d):
    if d == 0:
        return 1
    t = 0
    for mv in b.legal_moves:
        b.push(mv); t += cperft(b, d - 1); b.pop()
    return t


print('== perft 3')
random.seed(960)
for n in [518, 0, 959] + random.sample(range(960), 5):
    got, want = C.perft(C.Pos960(n), 3), cperft(chess.Board.from_chess960_pos(n), 3)
    check(got == want, '%3d %s: %d' % (n, C.letters(n), got))

print('== the legal moves at every ply of 300 random games (60 plies at most)')
plies = castles = 0
bad = []
for g in range(300):
    n = random.randrange(960)
    p, b = C.Pos960(n), chess.Board.from_chess960_pos(n)
    for k in range(60):
        ours = {uci(p, m): m for m in p.legal()}
        theirs = {mv for mv in b.legal_moves if mv.promotion in (None, chess.QUEEN)}
        if set(ours) != theirs or not same_board(p, b) or (p.sd > 0) != b.turn:
            bad.append((n, k, b.fen()))
            break
        if not theirs:
            break
        mv = random.choice(sorted(theirs, key=str))
        castles += b.is_castling(mv)
        p.make(ours[mv], 3); p.undo.pop(3)
        b.push(mv)
        plies += 1
check(not bad, '%d plies, %d castlings, the same moves and boards%s' % (plies, castles, '' if not bad else ' FIRST %s' % (bad[0],)))

print('== 4 games of the engine (level 2, 40 plies), its moves legal for python-chess')
for n in random.sample(range(960), 4):
    p, b = C.Pos960(n), chess.Board.from_chess960_pos(n)
    ok = True
    for k in range(40):
        m, v, nodes = p.search(2)
        if not m:
            break
        mv = uci(p, m)
        ok &= mv in b.legal_moves
        if not ok:
            break
        p.make(m, 3); b.push(mv)
        if b.is_game_over():
            break
    check(ok and same_board(p, b), '%3d %s: %d plies, %s' % (n, C.letters(n), len(b.move_stack), b.board_fen()))

print('\nALL PASSED' if not FAIL else '\n%d FAILED' % len(FAIL))
sys.exit(1 if FAIL else 0)
