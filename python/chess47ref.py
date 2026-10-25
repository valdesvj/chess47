"""chess47ref.py - the Chess 47 engine in Python, step for step the algorithm of programs_rem/CHESS47.txt, so the tests
can compare the two (the same moves in the same order, the same scores, the same choice). Also a plain perft to check
the move generator against the published counts.

Board: the 10 x 12 mailbox of the matrix BD (1 x 120, column s = 10 row + col + 1, rows 0-11, cols 0-9): the squares
a1 = 22 ... h1 = 29 ... a8 = 92 ... h8 = 99; the border holds OFF = 8. Pieces: 1 pawn, 2 knight, 3 bishop, 4 rook,
5 queen, 6 king; + white, - black; 0 empty. A move: from x 1000 + to (promotion: always a queen).
Castling rights: a 4-bit word (1 white short, 2 white long, 4 black short, 8 black long), as the 64-bit word of the
calculator (AND with a mask, BS? to test a bit). Score SC: material + piece-square value, white positive,
updated by each move (the search reads it as it is).

Search (depth 1 or 2, the side to move S):
  the root moves of S (castling included), captures first (a pass over the captures, then the quiet moves, each in
  the order they were generated); depth 1: a move that leaves S's king attacked is skipped; value S x SC.
  Depth 2: the replies of -S (no castling), captures first; value the least S x SC over them, a cut as soon as it
  is not above the best so far; a move that lets the king be taken (-20000) is so never chosen. No reply: S x SC.
  The first move with the highest value is played. Best < -10000: no legal move (mate or stalemate)."""
OFF = 8
V = (0, 100, 300, 320, 500, 900, 20000)
NOFF = (-21, -19, -12, -8, 8, 12, 19, 21)
DIRS = (-11, -9, 9, 11, -10, -1, 1, 10)          # Q, K: the diagonals (B), then the lines (R)
BDIR = (-11, -9, 9, 11)
RDIR = (-10, -1, 1, 10)


def file_of(s):
    return (s - 1) % 10 - 1                       # 0 a ... 7 h


def row_of(s):
    return (s - 1) // 10                          # 2 rank 1 ... 9 rank 8


def pst(t, s, c):
    """The piece-square value of a piece type t (1-6) of colour c (+1 / -1) on s (from its own side)."""
    f = file_of(s)
    r = row_of(s) - 2 if c > 0 else 9 - row_of(s)       # 0 its first rank ... 7 the last
    cen = 6 - (abs(2 * f - 7) + abs(2 * r - 7)) // 2    # 0 a corner ... 6 the four middle squares
    if t == 1:
        return 6 * (r - 1) + (8 if f in (3, 4) and 2 <= r <= 4 else 0)
    if t == 2:
        return 5 * cen - 15
    if t == 3:
        return 3 * cen - 6
    if t == 4:
        return 10 if r == 6 else 0
    if t == 5:
        return 2 * cen - 6
    return 10 - 4 * cen if r == 0 else -4 * cen


def value(p, s):
    """The signed value of piece p on s (the score of the square)."""
    if p == 0:
        return 0
    c = 1 if p > 0 else -1
    return c * (V[abs(p)] + pst(abs(p), s, c))


class Pos:
    def __init__(self):
        self.bd = [OFF] * 121                     # bd[1 .. 120]
        back = (4, 2, 3, 5, 6, 3, 2, 4)
        for f in range(8):
            self.bd[22 + f] = back[f]
            self.bd[32 + f] = 1
            for r in (42, 52, 62, 72):
                self.bd[r + f] = 0
            self.bd[82 + f] = -1
            self.bd[92 + f] = -back[f]
        self.sd, self.ep, self.cr = 1, 0, 15
        self.kw, self.kb = 26, 96
        self.sc = sum(value(self.bd[s], s) for s in range(22, 100) if self.bd[s] != OFF)
        self.undo = {}

    @classmethod
    def fen(cls, text):
        """A position from a FEN (for the tests)."""
        p = cls()
        parts = text.split()
        for s in range(22, 100):
            if p.bd[s] != OFF:
                p.bd[s] = 0
        rows = parts[0].split('/')
        for i, row in enumerate(rows):
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch); continue
                t = 'pnbrqk'.index(ch.lower()) + 1
                s = 10 * (9 - i) + f + 2
                p.bd[s] = t if ch.isupper() else -t
                f += 1
        p.sd = 1 if parts[1] == 'w' else -1
        p.cr = sum(b for ch, b in zip('KQkq', (1, 2, 4, 8)) if ch in parts[2])
        p.ep = 0 if parts[3] == '-' else 10 * (int(parts[3][1]) + 1) + 'abcdefgh'.index(parts[3][0]) + 2
        p.kw = p.bd.index(6); p.kb = p.bd.index(-6)
        p.sc = sum(value(p.bd[s], s) for s in range(22, 100) if p.bd[s] != OFF)
        return p

    # ---- attacked: is s attacked by colour c? ----
    def attacked(self, s, c):
        b = self.bd
        for d in (9, 11):                         # a pawn of c: from below (white) or above (black)
            if b[s - c * d] == c:
                return True
        for d in NOFF:
            t = s + d
            if 1 <= t <= 120 and b[t] == 2 * c:
                return True
        for d in DIRS:
            t = s + d
            if b[t] == 6 * c:
                return True
            diag = d in BDIR
            while b[t] == 0:
                t += d
            x = b[t] * c
            if x == 5 or x == (3 if diag else 4):
                return True
        return False

    # ---- the moves of colour c (castling when castle) ----
    def gen(self, c, castle=True):
        b, out = self.bd, []
        for s in range(22, 100):
            x = b[s] * c
            if b[s] == OFF or x <= 0:
                continue
            if x == 1:
                t = s + 10 * c
                if b[t] == 0:
                    out.append(s * 1000 + t)
                    if row_of(s) == (3 if c > 0 else 8) and b[t + 10 * c] == 0:
                        out.append(s * 1000 + t + 10 * c)
                for d in (9, 11):
                    t = s + d * c
                    y = b[t]
                    if (y != OFF and y * c < 0) or (t == self.ep and self.ep):
                        out.append(s * 1000 + t)
            elif x == 2:
                for d in NOFF:
                    t = s + d
                    y = b[t]
                    if y != OFF and y * c <= 0:
                        out.append(s * 1000 + t)
            elif x == 6:
                for d in DIRS:
                    t = s + d
                    y = b[t]
                    if y != OFF and y * c <= 0:
                        out.append(s * 1000 + t)
                if castle:
                    home = 26 if c > 0 else 96
                    bit = 1 if c > 0 else 4
                    if s == home and self.cr & bit and b[s + 1] == 0 and b[s + 2] == 0 and b[s + 3] == 4 * c \
                            and not self.attacked(s, -c) and not self.attacked(s + 1, -c) and not self.attacked(s + 2, -c):
                        out.append(s * 1000 + s + 2)
                    if s == home and self.cr & 2 * bit and b[s - 1] == 0 and b[s - 2] == 0 and b[s - 3] == 0 \
                            and b[s - 4] == 4 * c and not self.attacked(s, -c) and not self.attacked(s - 1, -c) \
                            and not self.attacked(s - 2, -c):
                        out.append(s * 1000 + s - 2)
            else:
                dirs = BDIR if x == 3 else RDIR if x == 4 else DIRS
                for d in dirs:
                    t = s + d
                    while True:
                        y = b[t]
                        if y == OFF or y * c > 0:
                            break
                        out.append(s * 1000 + t)
                        if y != 0:
                            break
                        t += d
        return out

    # ---- make / unmake (ply: the slot of the undo data) ----
    def make(self, m, ply):
        b = self.bd
        f, t = m // 1000, m % 1000
        x, y = b[f], b[t]
        c = 1 if x > 0 else -1
        self.undo[ply] = (m, x, y, self.ep, self.cr, self.sc)
        self.sc -= value(y, t) + value(x, f)
        b[f] = 0
        flag = 0
        if abs(x) == 1:
            if t == self.ep and y == 0:           # en passant: the pawn behind t
                cp = t - 10 * c
                self.sc -= value(b[cp], cp)
                b[cp] = 0
                flag = 1
            if row_of(t) == (9 if c > 0 else 2):
                x = 5 * c                         # promotion: a queen
        b[t] = x
        self.sc += value(x, t)
        if abs(x) == 6:
            if c > 0:
                self.kw = t
            else:
                self.kb = t
            if abs(t - f) == 2:                   # castling: the rook
                rf, rt = (f + 3, f + 1) if t > f else (f - 4, f - 1)
                self.sc += value(4 * c, rt) - value(4 * c, rf)
                b[rt], b[rf] = 4 * c, 0
                flag = 2
        self.ep = (f + t) // 2 if abs(x) == 1 and abs(t - f) == 20 else 0
        for sq, mask in ((26, 12), (22, 13), (29, 14), (96, 3), (92, 7), (99, 11)):
            if f == sq or t == sq:
                self.cr &= mask
        self.sd = -self.sd
        self.undo[ply] += (flag,)

    def unmake(self, ply):
        b = self.bd
        m, x, y, self.ep, self.cr, self.sc, flag = self.undo[ply]
        f, t = m // 1000, m % 1000
        c = 1 if x > 0 else -1
        b[f], b[t] = x, y
        if flag == 1:
            b[t - 10 * c] = -c
        if flag == 2:
            rf, rt = (f + 3, f + 1) if t > f else (f - 4, f - 1)
            b[rf], b[rt] = 4 * c, 0
        if abs(x) == 6:
            if c > 0:
                self.kw = f
            else:
                self.kb = f
        self.sd = -self.sd

    def king(self, c):
        return self.kw if c > 0 else self.kb

    def legal(self, c=None):
        """The legal moves of the side to move (castling included)."""
        c = c or self.sd
        out = []
        for m in self.gen(c):
            self.make(m, 3)
            if not self.attacked(self.king(c), -c):
                out.append(m)
            self.unmake(3)
        return out

    # ---- the search ----
    def search(self, depth):
        S = self.sd
        moves = self.gen(S)
        best, bm, nodes = -30000, 0, 0
        for cap in (True, False):
            for m in moves:
                if (self.bd[m % 1000] != 0) != cap:
                    continue
                self.make(m, 1)
                if depth == 1:
                    v = S * self.sc if not self.attacked(self.king(S), -S) else -30000
                    nodes += 1
                else:
                    replies = self.gen(-S, castle=False)
                    if not replies:
                        v = S * self.sc
                    else:
                        v, cut = 30000, False
                        for cap2 in (True, False):
                            for r in replies:
                                if (self.bd[r % 1000] != 0) != cap2:
                                    continue
                                self.make(r, 2)
                                w = S * self.sc
                                nodes += 1
                                self.unmake(2)
                                if w < v:
                                    v = w
                                if v <= best:
                                    cut = True
                                    break
                            if cut:
                                break
                self.unmake(1)
                if v > best:
                    best, bm = v, m
        return bm, best, nodes


def perft(p, depth):
    if depth == 0:
        return 1
    n = 0
    c = p.sd
    for m in p.gen(c):
        p.make(m, 10 + depth)
        if not p.attacked(p.king(c), -c):
            n += perft(p, depth - 1)
        p.unmake(10 + depth)
    return n


def name(s):
    return 'abcdefgh'[file_of(s)] + str(row_of(s) - 1)


def mname(m):
    return name(m // 1000) + name(m % 1000)


if __name__ == '__main__':
    import time
    for fen, want in (('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', (20, 400, 8902, 197281)),
                      ('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1', (48, 2039, 97862)),
                      ('8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1', (14, 191, 2812, 43238)),
                      ('r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1', (6, 264, 9467)),
                      ('rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8', (44, 1486, 62379))):
        p = Pos.fen(fen)
        got = tuple(perft(p, d + 1) for d in range(len(want)))
        print('perft %s %s %s' % (got, 'ok' if got == want else 'WANT %s' % (want,), fen))
    p = Pos()
    for d in (1, 2):
        t = time.time()
        m, v, n = p.search(d)
        print('start, depth %d: %s value %d, %d leaves (%.2f s)' % (d, mname(m), v, n, time.time() - t))
