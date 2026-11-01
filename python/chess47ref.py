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


ENGINE = ('mate', 'recap', 'mvv', 'killer')      # v0.3.4's search (v0.2: no killer; v0.1: none of them)


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
    def has_legal(self, c):
        """Has colour c (to move) a legal move? (the first one found ends the search; castling included)."""
        for m in self.gen(c):
            self.make(m, 4)
            ok = not self.attacked(self.king(c), -c)
            self.unmake(4)
            if ok:
                return True
        return False

    budget = None                                 # level 3's answers allowed (None: no limit; the C47: its 60 s)

    def search3(self, first=0):
        """Level 3 (CHESS47's LBL :THINK3:): the root moves (level 2's best one first), the replies of -S played (no
        castling; the killer first), and S's answers valued as level 2 values the replies, from S's side: S x SC after
        the answer, less the value of the piece that took when -S attacks its target (the recapture); the best legal
        answer (its legality tested only when it is the best so far). The cuts: the answers when the best reaches the
        least reply so far (beta), the replies when the least is not above the best root move (alpha)."""
        S = self.sd
        moves = self.order(self.gen(S))
        if first in moves:
            moves.remove(first)
            moves.insert(0, first)
        best, bm, nodes = -30000, 0, 0
        self.aborted = False
        self.killer = (0, 0, 0)
        self.akiller = (0, 0, 0)                  # the answer that cut the last reply (LBL :AKILL:)
        for m in moves:
            self.make(m, 1)
            if self.attacked(self.king(S), -S):
                v = -30000                                 # not legal: never chosen (LBL :ROOT3:)
            elif 'mate' in self.opts and self.attacked(self.king(-S), S) and not self.has_legal(-S):
                v = 29000
            else:
                replies = self.gen(-S, castle=False)
                if not replies:
                    v = S * self.sc
                else:
                    v = 30000
                    rs = self.order(replies)
                    if 'killer' in self.opts and self.killer_ok():
                        rs.remove(self.killer[0])
                        rs.insert(0, self.killer[0])
                    for r in rs:
                        x, y = self.bd[r // 1000], self.bd[r % 1000]
                        self.make(r, 2)
                        if abs(y) == 6:                   # the reply took S's king: lost, no answer
                            w, n = S * self.sc, 0
                        else:
                            w, n = self.answers(S, v)
                        nodes += n
                        self.unmake(2)
                        if w < v:
                            v = w
                        if v <= best:
                            self.killer = (r, x, y)
                            break
                        if self.budget is not None and nodes >= self.budget:
                            self.aborted, v = True, -30000     # LBL :TIME3: within the replies
                            break
            self.unmake(1)
            if v > best:
                best, bm = v, m
            if self.aborted or (self.budget is not None and nodes >= self.budget):
                self.aborted = True
                break
        return bm, best, nodes

    def answers(self, S, beta):
        """S's best answer (LBL :ANSW:): the most of S x SC after it (less the piece that took when -S can take back),
        over the legal answers, stopped as soon as it reaches beta; S x SC when S has no move; none legal: -29500 when S is
        in check (mate), else 0 (stalemate)."""
        moves = self.gen(S, castle=False)
        if not moves:
            return S * self.sc, 0
        if self.killer_ok(self.akiller):          # the answer killer first (it is then in the list: valued twice)
            moves = [self.akiller[0]] + moves
        amax, n = -30000, 0
        for a in moves:
            t = a % 1000
            cap = self.bd[t] != 0
            x, y = self.bd[a // 1000], self.bd[t]
            self.make(a, 3)
            n += 1
            w = S * self.sc
            if cap and self.attacked(t, -S):
                w -= abs(value(self.bd[t], t))
            if w > amax and not self.attacked(self.king(S), -S):
                amax = w
            self.unmake(3)
            if amax >= beta:
                self.akiller = (a, x, y)
                break
        if amax == -30000:                                 # no legal answer: mated, or stalemated
            amax = -29500 if self.attacked(self.king(S), -S) else 0
        return amax, n

    def killer_ok(self, killer=None):
        """Is the killer still a move of this position (as LBL :KILLER:)? Its piece on its square, its target as it
        was, the squares between empty for a bishop, rook, queen or a pawn's two steps; never en passant."""
        r, x, y = self.killer if killer is None else killer
        if not r:
            return False
        f, t = r // 1000, r % 1000
        b = self.bd
        if b[f] != x or b[t] != y:
            return False
        k = abs(x)
        if k == 1 and y == 0 and (t - f) % 10 != 0:
            return False
        if 3 <= k <= 5 or (k == 1 and abs(t - f) == 20):
            dr, dc = t // 10 - f // 10, t % 10 - f % 10
            step = 10 * ((dr > 0) - (dr < 0)) + (dc > 0) - (dc < 0)
            s = f + step
            while s != t:
                if b[s] != 0:
                    return False
                s += step
        return True

    def order(self, moves):
        """The captures by the value of the piece taken (queen first; the order generated among equals), then the
        other moves as generated (opts 'mvv'); else the captures, then the others, each as generated."""
        caps = [m for m in moves if self.bd[m % 1000] != 0]
        if 'mvv' in self.opts:
            caps = [m for k in (6, 5, 4, 3, 2, 1) for m in caps if abs(self.bd[m % 1000]) == k]
        return caps + [m for m in moves if self.bd[m % 1000] == 0]

    def search(self, depth, opts=None):
        """opts: 'mate' (level 2: a checking move after which the other side has no legal move scores 29000),
        'recap' (level 2: a capture reply on a square S attacks is answered by its recapture: + the value of the
        piece that took), 'mvv' (the captures by the value taken), 'killer' (level 2: the reply that cut the last
        root move is valued first when it is still possible, LBL :KILLER:; the answer is the same, found sooner)."""
        self.opts = set(opts if opts is not None else ENGINE)
        if depth == 3:
            first, v2, n2 = self.search(2, opts)
            m, v, n = self.search3(first)
            if self.budget is not None and self.aborted and m == 0:
                return first, v2, n                # not even the first root move done: level 2's move
            return m, v, n
        S = self.sd
        moves = self.order(self.gen(S))
        best, bm, nodes = -30000, 0, 0
        self.killer = (0, 0, 0)                   # the reply that cut, its piece, what stood on its target
        for m in moves:
            self.make(m, 1)
            if depth == 1:
                v = S * self.sc if not self.attacked(self.king(S), -S) else -30000
                nodes += 1
            elif 'mate' in self.opts and not self.attacked(self.king(S), -S) and self.attacked(self.king(-S), S) \
                    and not self.has_legal(-S):
                v = 29000
            else:
                replies = self.gen(-S, castle=False)
                if not replies:
                    v = S * self.sc
                else:
                    v = 30000
                    first = [self.killer[0]] if 'killer' in self.opts and self.killer_ok() else []
                    for r in first + self.order(replies):
                        cap = self.bd[r % 1000] != 0
                        x, y = self.bd[r // 1000], self.bd[r % 1000]
                        self.make(r, 2)
                        w = S * self.sc
                        nodes += 1
                        if cap and 'recap' in self.opts and self.attacked(r % 1000, S):
                            w += abs(value(self.bd[r % 1000], r % 1000))
                        self.unmake(2)
                        if w < v:
                            v = w
                        if v <= best:
                            self.killer = (r, x, y)
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


def san(p, m):
    """The move m of the position p (not played) in standard algebraic notation (FIDE, as CHESS47's move list):
    the piece letter (none for a pawn), the file or the rank or both of the square it leaves when another piece of
    the same kind could go there legally, x for a capture (a pawn: its file first), the target, =Q for a promotion,
    + for check, # for mate; castling O-O / O-O-O (a Chess960 position's castle_move too)."""
    f, t = m // 1000, m % 1000
    x = p.bd[f]
    k = abs(x)
    castle = p.castle_move(m) if hasattr(p, 'castle_move') else k == 6 and abs(t - f) == 2
    if castle:
        s = 'O-O' if t > f else 'O-O-O'
    elif k == 1:
        take = p.bd[t] != 0 or (t == p.ep and (t - f) % 10 != 0)
        s = ('abcdefgh'[file_of(f)] + 'x' if take else '') + name(t)
        if row_of(t) in (2, 9):
            s += '=Q'
    else:
        s = ' PNBRQK'[k]
        if k != 6:
            others = [o // 1000 for o in p.legal() if o % 1000 == t and o // 1000 != f and p.bd[o // 1000] == x]
            if others:
                if all(file_of(o) != file_of(f) for o in others):
                    s += 'abcdefgh'[file_of(f)]
                elif all(row_of(o) != row_of(f) for o in others):
                    s += str(row_of(f) - 1)
                else:
                    s += name(f)
        s += ('x' if p.bd[t] != 0 else '') + name(t)
    p.make(m, 9)
    if p.attacked(p.king(p.sd), -p.sd):
        s += '+' if p.has_legal(p.sd) else '#'
    p.unmake(9)
    return s


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
