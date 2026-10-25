#!/usr/bin/env python3
"""match47.py - matches of CHESS47 (build/CHESS47.txt, in the C47 simulator) against an independent opponent: a
python-chess player (2 plies, material, the moves of equal value at random). The opponent's moves are keyed as you
would (the cursor 8 2 4 6 from where it is, 5 on the piece, 5 on the target); the C47 thinks at level 2 with its book.

Checked in every game: each move of the C47 is legal (python-chess), the game ends as the rules say (the C47's
CHECKMATE / STALEMATE / DRAW when python-chess sees a mate, a stalemate, a threefold repetition or no mating
material), and the board of the C47 is the one of python-chess after every move. A game over 120 plies stops:
the material decides it (3 points or more), else a draw.
  python3 tools/match47.py [games] [first seed]     -> docs/MATCHES.md (the results and the games)"""
import os, random, sys, time
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import chess                                                     # noqa: E402
import c47sim                                                    # noqa: E402
import chess47sim as S                                           # noqa: E402

VALS = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 320, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
MAXPLY = 120


def sq(s):
    """A square of the mailbox -> python-chess."""
    return chess.square((s - 1) % 10 - 1, (s - 1) // 10 - 2)


def mb(q):
    return 10 * (chess.square_rank(q) + 2) + chess.square_file(q) + 2


def opponent(b, rnd):
    def ev(bb):
        return sum(VALS[p.piece_type] * (1 if p.color == bb.turn else -1) for p in bb.piece_map().values())
    best, cands = -10 ** 9, []
    for m in b.legal_moves:
        if m.promotion and m.promotion != chess.QUEEN:
            continue
        b.push(m)
        if b.is_checkmate():
            worst = 10 ** 6
        else:
            worst = 10 ** 9
            for r in b.legal_moves:
                b.push(r)
                worst = min(worst, -ev(b) if not b.is_checkmate() else -10 ** 6)
                b.pop()
            if worst == 10 ** 9:
                worst = 0
        b.pop()
        if worst > best:
            best, cands = worst, [m]
        elif worst == best:
            cands.append(m)
    return rnd.choice(cands)


def keys_for(cursor, frm, to):
    out = []
    for a, b in ((cursor, frm), (frm, to)):
        dr, df = (b - 1) // 10 - (a - 1) // 10, (b - 1) % 10 - (a - 1) % 10
        out += [S.UP if dr > 0 else S.DOWN] * abs(dr) + [S.RIGHT if df > 0 else S.LEFT] * abs(df) + [S.PICK]
    return out


def game(seed, c47_white):
    rnd = random.Random(seed)
    b = chess.Board()
    c = c47sim.load([S.PROG])
    c.s = [D(0)] * 4; c.pix = []; c.keys = []; c.steps = 0; c.frames = []
    c.seed = seed                                                # RAN#: the book's choice
    st = {'synced': 0, 'over': False, 'err': None, 'first': True, 'c47moves': 0, 'c47steps': 0, 'last': 0}

    def sync():
        """The moves of the game record GH not yet on b: pushed, each one legal."""
        row = c.mats['GH'][0]
        while st['synced'] < len(row) and int(row[st['synced']]):
            m = int(row[st['synced']])
            f, t = sq(m // 1000), sq(m % 1000)
            mv = chess.Move(f, t)
            if b.piece_at(f) and b.piece_at(f).piece_type == chess.PAWN and chess.square_rank(t) in (0, 7):
                mv = chess.Move(f, t, chess.QUEEN)
            if mv not in b.legal_moves:
                st['err'] = 'illegal move %s in %s' % (mv.uci(), b.fen()); raise StopIteration
            b.push(mv)
            st['synced'] += 1

    def hook(op, x):
        if op != 'KEY?' or c.keys:
            return
        if st['first']:                                          # the start: the C47 takes white with +
            st['first'] = False
            if c47_white:
                c.keys = [S.HAND]; return
        sync()
        bd = S.board(c)
        for q in chess.SQUARES:                                  # the C47's board is python-chess's
            p = b.piece_at(q)
            want = 0 if p is None else (p.piece_type if p.color else -p.piece_type)
            if bd[mb(q)] != want:
                st['err'] = 'board differs at %s: %s, python-chess %s' % (chess.square_name(q), bd[mb(q)], want)
                raise StopIteration
        if int(c.reg.get('97', 0)) or b.ply() >= MAXPLY:
            st['over'] = bool(int(c.reg.get('97', 0)))
            c.keys = [S.END]; return
        if b.is_game_over(claim_draw=True):
            st['err'] = 'the C47 did not see the end: %s' % b.result(claim_draw=True); raise StopIteration
        m = opponent(b, rnd)
        c.keys = keys_for(int(c.reg['28']), mb(m.from_square), mb(m.to_square))
    c.count = hook
    t0 = time.time()
    try:
        c.run('CHESS47', maxsteps=10 ** 10)
    except StopIteration:
        pass
    if st['err'] is None and 'GH' in c.mats:
        try:
            sync()
        except StopIteration:
            pass
    res = b.result(claim_draw=True)
    how = ('checkmate' if b.is_checkmate() else 'stalemate' if b.is_stalemate() else 'repetition'
           if b.can_claim_threefold_repetition() else 'material' if b.is_insufficient_material() else '')
    if res == '*':
        mat = sum(VALS[p.piece_type] // 100 * (1 if p.color else -1) for p in b.piece_map().values())
        res, how = ('1-0' if mat >= 3 else '0-1' if mat <= -3 else '1/2-1/2'), 'adjudicated at %d plies (material %+d)' % (b.ply(), mat)
    if how in ('checkmate', 'stalemate', 'repetition', 'material') and not st['over'] and st['err'] is None:
        st['err'] = 'python-chess sees %s, the C47 did not stop' % how
    score = {'1-0': 1, '0-1': 0, '1/2-1/2': 0.5}[res]
    score = score if c47_white else 1 - score
    return dict(seed=seed, white=c47_white, result=res, how=how, score=score, plies=b.ply(), err=st['err'],
                san=chess.Board().variation_san(b.move_stack), secs=time.time() - t0, steps=c.steps)


def main():
    import chess.pgn  # noqa: F401
    n = int(sys.argv[1]) if sys.argv[1:] else 10
    s0 = int(sys.argv[2]) if sys.argv[2:] else 1
    out, tot = [], 0
    for g in range(n):
        r = game(s0 + g, g % 2 == 0)
        tot += r['score']
        line = '%2d  C47 %s  %-7s %-40s %5.1f  %3d plies  %s' % (g + 1, 'white' if r['white'] else 'black', r['result'],
                                                             r['how'], r['score'], r['plies'], r['err'] or 'all moves legal, the end right')
        print(line, flush=True)
        out.append((r, line))
    bad = sum(1 for r, _ in out if r['err'])
    md = ['# CHESS47 matches', '',
          'CHESS47 (level 2, its book) in the C47 simulator against a python-chess player (2 plies, material, random among',
          'equals), `python3 tools/match47.py %d %d`. Every move of the C47 checked legal, the board checked after every'
          % (n, s0), 'move, the end of each game checked against the rules (python-chess). Over %d plies: material.' % MAXPLY, '',
          '**Score of the C47: %s / %d**, %d game(s) with a problem.' % (('%g' % tot), n, bad), '', '```']
    md += [ln for _, ln in out] + ['```', '']
    for r, _ in out:
        md += ['## Game %d: C47 %s, %s (%s)' % (out.index((r, _)) + 1, 'white' if r['white'] else 'black', r['result'], r['how']),
               '', r['san'], '']
    open(os.path.join(ROOT, 'docs', 'MATCHES.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('score %g / %d, %d problem(s); docs/MATCHES.md' % (tot, n, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
