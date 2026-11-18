"""influence.py - a prototype for CHESS47: the influence (attack) maps of both sides in the leaf evaluation of level 2,
in Python first, to measure what it is worth before anything is written in RPN (branch claude/chess47-influence).

The maps: for each of the 64 squares, how many pieces of each colour attack it and the value of the cheapest one
(pawns diagonally, knights, kings, and the sliding pieces up to and including the first piece on the ray). From them,
at a leaf of the level-2 search (after S's root move and -S's reply, S to move), seen from S:

  threats   a piece P (value v, not a king) of a colour A is under threat when the other colour attacks its square
            and either A does not defend it (threat v) or the cheapest attacker is worth less (threat v - attacker).
            S is to move: S can take its best threat (+ T_OWN x the largest of S's threats), and can save one of its
            own pieces, not two (- T_FORK x the second largest of -S's threats; - T_ONE x the largest, as S may have to
            spend its move on it).
  control   each square counts for the side with more attackers: C_CENTRE for d4 e4 d5 e5, C_WIDE for the 12 around
            them, C_KING for the 8 squares around the other side's king (and minus for those around one's own), 1 else
            (x C_ALL).

The search is the twin's (python/chess47ref.py, unchanged: Pos.search) with the leaf value S x SC (+ the recapture)
plus influence(S); the opening book and everything else as CHESS47. WEIGHTS can be changed for a test.
  InfPos.fen(...).search(2)          the move, its value, the leaves (as chess47ref)
  InfPos.maps_built                  how many leaves built the two maps (the cost a C47 port would pay)"""
import chess47ref as R

WEIGHTS = {'T_OWN': 0.5, 'T_ONE': 0.25, 'T_FORK': 0.75, 'C_ALL': 2.0, 'C_CENTRE': 4, 'C_WIDE': 2, 'C_KING': 5}
# C_ALL 2: the best of the tests (docs/INFLUENCE.md: 1 -> +64, 2 -> +79, 3 -> +68 at the root, 710 games each)
PVAL = {1: 100, 2: 300, 3: 320, 4: 500, 5: 900, 6: 2000}       # a king attacks as the dearest piece
SQUARES = [s for s in range(22, 100) if 1 <= (s - 1) % 10 <= 8]
CENTRE = {55, 56, 65, 66}
WIDE = {s for s in SQUARES if 3 <= (s - 1) % 10 <= 6 and 4 <= (s - 1) // 10 <= 7} - CENTRE
KAROUND = (-11, -10, -9, -1, 1, 9, 10, 11)


def maps(b):
    """The influence maps of the board b (the mailbox): cnt[c][s] the attackers of colour c (c = 1 white, -1 black)
    on s, low[c][s] the value of the cheapest one."""
    cnt = {1: {}, -1: {}}
    low = {1: {}, -1: {}}

    def hit(c, t, v):
        cnt[c][t] = cnt[c].get(t, 0) + 1
        if v < low[c].get(t, 99999):
            low[c][t] = v

    for s in SQUARES:
        p = b[s]
        if p == 0:
            continue
        c, k = (1 if p > 0 else -1), abs(p)
        v = PVAL[k]
        if k == 1:
            for d in (9, 11):
                t = s + c * d
                if b[t] != R.OFF:
                    hit(c, t, v)
        elif k == 2:
            for d in R.NOFF:
                t = s + d
                if 1 <= t <= 120 and b[t] != R.OFF:
                    hit(c, t, v)
        elif k == 6:
            for d in R.DIRS:
                if b[s + d] != R.OFF:
                    hit(c, s + d, v)
        else:
            dirs = R.BDIR if k == 3 else R.RDIR if k == 4 else R.DIRS
            for d in dirs:
                t = s + d
                while b[t] != R.OFF:
                    hit(c, t, v)
                    if b[t] != 0:
                        break
                    t += d
    return cnt, low


def influence(b, S, w=None, skip=0, tomove=True):
    """The influence term from S's side (S to move) for the board b (skip: a square whose take-back the search has
    already counted, the recapture: not a threat of S again)."""
    w = w or WEIGHTS
    cnt, low = maps(b)
    own, other = [], []                                    # S's threats, -S's threats
    for s in SQUARES:
        p = b[s]
        if p == 0 or abs(p) == 6:
            continue
        a = 1 if p > 0 else -1                             # the owner
        if s not in cnt[-a] or s == skip:
            continue
        v = PVAL[abs(p)]
        t = v if s not in cnt[a] else v - low[-a][s]
        if t > 0:
            (own if a == -S else other).append(t)
    own.sort(reverse=True)
    other.sort(reverse=True)
    x = 0.0
    if tomove:
        if own:
            x += w['T_OWN'] * own[0]
        if other:
            x -= w['T_ONE'] * other[0]
        if len(other) > 1:
            x -= w['T_FORK'] * other[1]
    elif len(own) > 1:                                     # -S to move (the root variant): -S saves one, a fork of S
        x += w['T_FORK'] * own[1]                          # wins the other; -S's own takes are the replies' business
    kings = {1: b.index(6) if 6 in b else 0, -1: b.index(-6) if -6 in b else 0}
    ctl = 0
    for s in SQUARES:
        n = cnt[S].get(s, 0) - cnt[-S].get(s, 0)
        if n == 0:
            continue
        side = 1 if n > 0 else -1
        wt = w['C_CENTRE'] if s in CENTRE else w['C_WIDE'] if s in WIDE else 1
        ctl += side * wt
    for c in (S, -S):
        k = kings[-c]                                      # the squares around c's opponent's king
        if not k:
            continue
        for d in KAROUND:
            t = k + d
            if b[t] != R.OFF and cnt[c].get(t, 0) > cnt[-c].get(t, 0):
                ctl += (1 if c == S else -1) * w['C_KING']
    return x + w['C_ALL'] * ctl


def bits_term(b, S, w=None):
    """The bitboard version (what CHESS47 can compute with 64-bit words): A[c] the squares colour c attacks at all (no
    counts); a square counts for S when only S attacks it. 2 x (the squares only S attacks - those only -S attacks,
    the centre 3 more, the 12 around it 1 more, the squares around the other king 5 more (each side)). Kings off the
    board (a king taken) give no zone."""
    w = w or WEIGHTS
    cnt, low = maps(b)
    cap = int(w.get('CAP', 1))                 # counts kept up to cap (bit-sliced words: >= 1, >= 2, ...)
    cS = {s: min(n, cap) for s, n in cnt[S].items()}
    cX = {s: min(n, cap) for s, n in cnt[-S].items()}
    sq = set(cS) | set(cX)
    oS = {s for s in sq if cS.get(s, 0) > cX.get(s, 0)}
    oX = {s for s in sq if cX.get(s, 0) > cS.get(s, 0)}
    zone = {}
    for c in (1, -1):
        k = b.index(6 * c) if 6 * c in b else 0
        zone[c] = {k + d for d in KAROUND if k and b[k + d] != R.OFF}
    t = (len(oS) - len(oX)) + (w['C_CENTRE'] - 1) * (len(oS & CENTRE) - len(oX & CENTRE)) \
        + (w['C_WIDE'] - 1) * (len(oS & WIDE) - len(oX & WIDE)) + w['C_KING'] * (len(oS & zone[-S]) - len(oX & zone[S]))
    return w['C_ALL'] * t


class InfPos(R.Pos):
    """The twin with the influence term at the leaves of level 2 (the search is copied from R.Pos.search, depth 2,
    with the one change marked)."""
    maps_built = 0
    weights = None
    variant = 'leaf'               # 'leaf': the maps at every leaf; 'root': once after each root move (-S to move),
                                   # the same term for all its replies (about 40 maps a move instead of about 80-400)

    def search(self, depth, opts=None):
        if depth != 2:
            return R.Pos.search(self, depth, opts)
        self.opts = set(opts if opts is not None else R.ENGINE)
        S = self.sd
        moves = self.order(self.gen(S))
        best, bm, nodes = -30000, 0, 0
        self.killer = (0, 0, 0)
        for m in moves:
            self.make(m, 1)
            if 'mate' in self.opts and not self.attacked(self.king(S), -S) and self.attacked(self.king(-S), S) \
                    and not self.has_legal(-S):
                v = 29000
            else:
                rootterm = 0
                if self.variant == 'root':
                    rootterm = influence(self.bd, S, self.weights, tomove=False)
                    InfPos.maps_built += 1
                elif self.variant == 'bits':
                    rootterm = bits_term(self.bd, S, self.weights)
                    InfPos.maps_built += 1
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
                        skip = 0
                        if cap and abs(y) != 6 and 'recap' in self.opts and self.attacked(r % 1000, S):
                            # (abs(y) != 6: not when the reply took S's king; the twin and CHESS47 v0.7.0 add the
                            # taking king's 20 000 there, so a king move next to the other king can look legal)
                            w += abs(R.value(self.bd[r % 1000], r % 1000))
                            skip = r % 1000
                        if abs(w) < 10000:                 # the change: the influence term (no king taken)
                            if self.variant in ('root', 'bits'):
                                w += rootterm
                            else:
                                w += influence(self.bd, S, self.weights, skip)
                                InfPos.maps_built += 1
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
