"""chess960.py - Chess960 (Fischer random chess) on the engine of chess47ref.py, for tools/play47.py.

chess47ref.Pos is the twin of CHESS47 (step for step) and is not changed: Pos960 is a subclass that adds what
Chess960 changes, and nothing else.
  start(n)    the back rank of the position n (0-959, the standard numbering of Scharnagl; 518 is normal chess)
  Pos960(n)   the start position n. Castling is the move king -> its own rook (the usual Chess960 input): the king
              ends on g (short, the rook on the king's right) or c (long), the rook on f or d; every square between
              the king, the rook and their targets empty (but those two), the king not attacked on its way (its
              square and its target included). The rights are lost when the king moves or that rook moves or is taken.
  The search (chess47ref.Pos.search) is the same: the levels play as in CHESS47.
python3 python/chess960.py   checks the move counts (perft) of positions against python-chess, when it is there."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chess47ref import Pos, OFF, value, ENGINE

KNIGHTS = ((0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4))


def start(n):
    """The back rank (piece kinds a-h: 2 N, 3 B, 4 R, 5 Q, 6 K) of the Chess960 position n."""
    if not 0 <= n <= 959:
        raise ValueError('a Chess960 position is 0-959')
    rank = [0] * 8
    n, b = divmod(n, 4)
    rank[2 * b + 1] = 3                               # the bishop on a light square (b d f h)
    n, b = divmod(n, 4)
    rank[2 * b] = 3                                   # the bishop on a dark square (a c e g)
    n, q = divmod(n, 6)
    rank[[f for f in range(8) if rank[f] == 0][q]] = 5
    empty = [f for f in range(8) if rank[f] == 0]
    for k in KNIGHTS[n]:
        rank[empty[k]] = 2
    for f, t in zip([f for f in range(8) if rank[f] == 0], (4, 6, 4)):
        rank[f] = t                                   # R K R in the three squares left
    return rank


def letters(n):
    return ''.join(' PNBRQK'[t] for t in start(n))


class Pos960(Pos):
    def __init__(self, n=518):
        super().__init__()
        self.n = n
        back = start(n)
        for f in range(8):
            self.bd[22 + f], self.bd[92 + f] = back[f], -back[f]
        k = back.index(6)
        rooks = [f for f in range(8) if back[f] == 4]
        self.kw, self.kb = 22 + k, 92 + k
        # the squares where the rights are lost: the kings, the rooks (short: the bits 1 / 4, long: 2 / 8)
        self.home = {1: 22 + k, -1: 92 + k}
        self.rook = {1: {1: 22 + rooks[1], 2: 22 + rooks[0]}, -1: {4: 92 + rooks[1], 8: 92 + rooks[0]}}
        self.sc = sum(value(self.bd[s], s) for s in range(22, 100) if self.bd[s] != OFF)

    def castle_move(self, m):
        """Is m a castling (the king onto its own rook)?"""
        f, t = m // 1000, m % 1000
        x, y = self.bd[f], self.bd[t]
        return abs(x) == 6 and y == 4 * (1 if x > 0 else -1)

    @staticmethod
    def targets(k, r):
        """The king's and the rook's squares after castling with the rook on r."""
        base = 22 if k < 30 else 92
        return (base + 6, base + 5) if r > k else (base + 2, base + 3)

    def gen(self, c, castle=True):
        """As chess47ref's gen, with Chess960's castling where CHESS47 makes it: right after the king's own moves (the
        squares are scanned a1 ... h8), short (the rook on the king's right) before long."""
        out = super().gen(c, castle=False)           # the moves of normal chess, castling left out
        if castle:
            b, k = self.bd, self.king(c)
            cast = []
            for bit, r in sorted(self.rook[c].items()):
                if not self.cr & bit or k != self.home[c] or b[r] != 4 * c:
                    continue
                kt, rt = self.targets(k, r)
                span = range(min(k, r, kt, rt), max(k, r, kt, rt) + 1)
                if any(b[s] != 0 and s not in (k, r) for s in span):
                    continue
                b[r] = 0                              # the rook does not shield the king's way
                safe = not any(self.attacked(s, -c) for s in range(min(k, kt), max(k, kt) + 1))
                b[r] = 4 * c
                if safe:
                    cast.append(k * 1000 + r)
            i = sum(1 for m in out if m // 1000 <= k)
            out[i:i] = cast
        return out

    def order(self, moves):
        """As chess47ref (the captures first, by the piece taken); castling (onto its own rook) is a quiet move, in
        its place among them (CHESS47's LBL :ADDC:)."""
        b = self.bd
        caps = [m for m in moves if b[m % 1000] != 0 and not self.castle_move(m)]
        if 'mvv' in getattr(self, 'opts', ENGINE):
            caps = [m for k in (6, 5, 4, 3, 2, 1) for m in caps if abs(b[m % 1000]) == k]
        return caps + [m for m in moves if m not in caps]

    def make(self, m, ply):
        b = self.bd
        f, t = m // 1000, m % 1000
        cr = self.cr
        if self.castle_move(m):
            x = b[f]
            c = 1 if x > 0 else -1
            kt, rt = self.targets(f, t)
            self.undo[ply] = (m, x, b[t], self.ep, self.cr, self.sc, 3)
            self.sc -= value(x, f) + value(4 * c, t)
            b[f] = b[t] = 0
            b[kt], b[rt] = x, 4 * c
            self.sc += value(x, kt) + value(4 * c, rt)
            if c > 0:
                self.kw = kt
            else:
                self.kb = kt
            self.ep = 0
            self.cr &= 12 if c > 0 else 3
            self.sd = -self.sd
            return
        super().make(m, ply)
        # the rights by this position's squares (chess47ref's are those of normal chess)
        for c, bits in ((1, 3), (-1, 12)):
            if f == self.home[c]:
                cr &= 15 - bits
            for bit, r in self.rook[c].items():
                if f == r or t == r:
                    cr &= 15 - bit
        self.cr = cr

    def unmake(self, ply):
        m, x, y, ep, cr, sc, flag = self.undo[ply]
        if flag != 3:
            return super().unmake(ply)
        b = self.bd
        f, t = m // 1000, m % 1000
        c = 1 if x > 0 else -1
        kt, rt = self.targets(f, t)
        b[kt] = b[rt] = 0
        b[f], b[t] = x, 4 * c
        if c > 0:
            self.kw = f
        else:
            self.kb = f
        self.ep, self.cr, self.sc = ep, cr, sc
        self.sd = -self.sd

    def fen_board(self):
        rows = []
        for r in range(9, 1, -1):
            row, e = '', 0
            for f in range(8):
                p = self.bd[10 * r + f + 2]
                if p == 0:
                    e += 1
                    continue
                row += (str(e) if e else '') + ' PNBRQK'[abs(p)].lower() if p < 0 else (str(e) if e else '') + ' PNBRQK'[p]
                e = 0
            rows.append(row + (str(e) if e else ''))
        return '/'.join(rows)


def perft(p, depth):
    if depth == 0:
        return 1
    n = 0
    for m in p.legal():
        p.make(m, 10 + depth)
        n += perft(p, depth - 1)
        p.unmake(10 + depth)
    return n


if __name__ == '__main__':
    import chess, random
    bad = 0
    for n in list(range(960)):
        if letters(n) != chess.Board.from_chess960_pos(n).board_fen().split('/')[-1]:
            bad += 1
    print('the 960 back ranks as python-chess:', 'ok' if bad == 0 else '%d differ' % bad)

    def cperft(b, d):
        if d == 0:
            return 1
        t = 0
        for mv in b.legal_moves:
            b.push(mv); t += cperft(b, d - 1); b.pop()
        return t
    random.seed(47)
    for n in [518, 0, 959] + random.sample(range(960), 12):
        p, b = Pos960(n), chess.Board.from_chess960_pos(n)
        got, want = perft(p, 3), cperft(b, 3)
        print('%3d %s perft 3: %d %s' % (n, letters(n), got, 'ok' if got == want else 'WANT %d' % want))
