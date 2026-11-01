"""play47.py - Chess 47 on the computer: the C47's screen (the same glyphs, fonts and places as CHESS47, the LCD's
colours), the same engine (python/chess47ref.py, the twin of CHESS47) and, new here, Chess960.

    pip install pygame            (python-chess is not needed to play)
    python3 tools/play47.py       a window of the C47's screen, 3 pixels a C47 pixel (--scale 2, 4 ...)
    python3 tools/play47.py --new        a new game (else the last one goes on: ~/.chess47_play.json)

The keys are the C47's (the number row or the keypad; the arrows and Enter too):
    8 2 4 6   the cursor (or the arrows)       5   pick a piece / play it there (or Enter, Space)
    +   swap sides        9   C47 vs C47 (again: you take the side to move)       3   two players
    7   a new game (normal chess)       /   a new Chess960 game: type its number 0-959 and Enter (Enter alone: a
        random one; 518 is normal chess; Esc: back)       1   the level (2, 1, CRAZY)       0 or Esc   the end
Castling in Chess960: pick the king, then its own rook (the king goes to g or c, the rook to f or d; the king's
target works too when it is not a normal king move). In normal chess: the king two squares, as on the C47.
The rules as CHESS47: mate, stalemate, the third repetition, too little material (no pawn, rook or queen and at
most one knight or bishop), a promotion is a queen; the clock (people only): 5 minutes and 10 s a move, the
time-out as FIDE 6.9 (a draw when the other side cannot mate). The book (normal chess only) as CHESS47's.

python3 tools/play47.py --shot FILE.png --keys "5 8 8 5 ..."   no window: the keys (the C47's, and ENTER ESC
    LEFT RIGHT UP DOWN, R for a random 960) one by one, the C47's moves at once, then the screen into FILE.png."""
import argparse, json, os, random, sys, time
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import book
import c47sim
import chess47ref as R
import chess960 as C
import layout as L

W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)          # as python/chess47sim.py (the pictures in docs/)
SAVE = os.path.expanduser('~/.chess47_play.json')
START_TIME, BONUS = 3000, 100                            # tenths of a second: 5 minutes, 10 s a move
LEVELS = {2: '2', 1: '1', 0: 'CRAZY'}


# ---- the screen: pixels (x, y), y 0 = the bottom row (as AGRAPH and ATEXT) ----
class _Text:
    pass


def text(pix, x, y, s, font=21):
    """ATEXT of the C47 at x, y (the simulator's own routine: the same fonts and places)."""
    t = _Text()
    t.s, t.pix, t.grfnt, t.grmod = [D(x), D(y), D(0), D(0)], [], font, 0
    c47sim.Calc.atext(t, s)
    pix |= {(col, row) for row, col in t.pix}


def words_at(pix, x, y, words, invert=False, full=L.FULL):
    """AGRAPH words (bit i = the row y + i) in the columns x, x + 1, ..."""
    for j, w in enumerate(words):
        if invert:
            w = ~w & full
        for i in range(L.SQ):
            if w >> i & 1:
                pix.add((x + j, y + i))


class Game:
    def __init__(self):
        self.level, self.me = 2, 1
        self.new(None)

    # ---- a game ----
    def new(self, n):
        """n None: normal chess (chess47ref.Pos, the book); else the Chess960 position n."""
        self.n = n
        self.pos = R.Pos() if n is None else C.Pos960(n)
        self.moves, self.texts, self.keys = [], [], [self.key()]
        self.tw = self.tb = START_TIME
        self.over, self.picked, self.prompt = None, None, None
        self.cursor = 36 if self.me != -1 else 86
        self.status = None
        self.last = time.time()

    def key(self):
        return tuple(self.pos.bd[22:100]) + (self.pos.sd,)

    def human(self, c):
        return self.me == c or self.me == 2

    def flipped(self):
        return self.me == -1

    def play(self, m, by_person):
        p = self.pos
        f, t = m // 1000, m % 1000
        castle = self.n is not None and p.castle_move(m)
        name = ('O-O' if t > f else 'O-O-O') if castle else R.name(f) + R.name(t)
        side = p.sd
        k = len(self.moves)
        self.texts.append(('%d. ' % (k // 2 + 1) if side > 0 else '%d... ' % (k // 2 + 1)) + name)
        p.make(m, 3)
        p.undo.pop(3, None)
        self.moves.append(m)
        self.keys.append(self.key())
        if by_person:
            if side > 0:
                self.tw += BONUS
            else:
                self.tb += BONUS
        self.picked = None
        self.status = None
        self.ending()

    def ending(self):
        p = self.pos
        if not p.legal():
            self.over = 'CHECKMATE' if p.attacked(p.king(p.sd), -p.sd) else 'STALEMATE'
        elif self.keys.count(self.keys[-1]) >= 3:
            self.over = 'DRAW: REPETITION'
        else:
            pcs = [abs(x) for x in p.bd[22:100] if x not in (0, R.OFF)]
            if not any(x in (1, 4, 5) for x in pcs) and sum(x in (2, 3) for x in pcs) <= 1:
                self.over = 'DRAW: MATERIAL'

    def can_mate(self, w):
        """FIDE 6.9 (as CHESS47's TMAT and python-chess's has_insufficient_material): can colour w mate at all?"""
        b = self.pos.bd
        mine = [abs(b[s]) for s in range(22, 100) if b[s] not in (0, R.OFF) and b[s] * w > 0 and abs(b[s]) != 6]
        other = [abs(b[s]) for s in range(22, 100) if b[s] not in (0, R.OFF) and b[s] * w < 0 and abs(b[s]) != 6]
        if any(x in (1, 4, 5) for x in mine):
            return True
        if 2 in mine:
            return not (len(mine) == 1 and all(x == 5 for x in other))
        if 3 in mine:
            colours = {(R.file_of(s) + R.row_of(s)) % 2 for s in range(22, 100) if abs(b[s]) == 3}
            return len(colours) > 1 or any(abs(b[s]) in (1, 2) for s in range(22, 100) if b[s] != R.OFF)
        return False

    def tick(self):
        """The clock of the side to move, when a person plays it."""
        now = time.time()
        dt, self.last = int((now - self.last) * 10), self.last + int((now - self.last) * 10) / 10
        if self.over or self.prompt or not self.human(self.pos.sd) or dt <= 0:
            return
        if self.pos.sd > 0:
            self.tw = max(0, self.tw - dt)
        else:
            self.tb = max(0, self.tb - dt)
        if min(self.tw, self.tb) == 0:
            lost = 1 if self.tw == 0 else -1
            self.over = 'DRAW: TIME, NO MATE' if not self.can_mate(-lost) else \
                ('WHITE' if lost > 0 else 'BLACK') + ' LOST ON TIME'

    # ---- the C47's move ----
    def c47_move(self):
        p = self.pos
        if self.n is None and len(self.moves) < 10:
            cands = [m for m in book.candidates(self.moves) if m in p.legal()]
            if cands:
                return random.choice(cands)
        if self.level == 0:
            return random.choice(p.legal())
        m, v, nodes = p.search(self.level)
        return m

    def c47_turn(self):
        return not self.over and not self.prompt and not self.human(self.pos.sd)

    # ---- the keys ----
    def press(self, k):
        if self.prompt is not None:
            return self.prompt_key(k)
        if k in ('0', 'ESC'):
            return 'quit'
        if k == '7':
            self.new(None)
        elif k == '/':
            self.prompt = ''
        elif k == '1':
            self.level = {2: 1, 1: 0, 0: 2}[self.level]
        elif k == '+':
            if self.me in (1, -1):
                self.me = -self.me
            else:
                self.me = self.pos.sd
            self.cursor_home()
        elif k == '9':
            self.me = self.pos.sd if self.me == 0 else 0
            self.picked = None
        elif k == '3':
            self.me = 1 if self.me == 2 else 2
            self.picked = None
        elif k in ('8', '2', '4', '6', 'UP', 'DOWN', 'LEFT', 'RIGHT'):
            d = {'8': 10, 'UP': 10, '2': -10, 'DOWN': -10, '4': -1, 'LEFT': -1, '6': 1, 'RIGHT': 1}[k]
            if self.flipped():
                d = -d
            t = self.cursor + d
            if self.pos.bd[t] != R.OFF:
                self.cursor = t
        elif k in ('5', 'ENTER'):
            self.pick()

    def cursor_home(self):
        self.cursor = 36 if self.me != -1 else 86
        self.picked = None

    def prompt_key(self, k):
        if k == 'ESC':
            self.prompt = None
        elif k == 'BACK':
            self.prompt = self.prompt[:-1]
        elif k.isdigit() and len(self.prompt) < 3:
            self.prompt += k
        elif k in ('ENTER', 'R'):
            n = int(self.prompt) if self.prompt and k == 'ENTER' else random.randrange(960)
            self.prompt = None
            if n <= 959:
                self.new(n)
            else:
                self.status = '960: 0 TO 959'

    def pick(self):
        p, s = self.pos, self.cursor
        if self.over or not self.human(p.sd):
            return
        x = p.bd[s]
        if self.picked is None or (x * p.sd > 0 and not self.castling_to(s)):
            if x * p.sd > 0:
                self.picked, self.status = s, None
            return
        if s == self.picked:
            self.picked = None
            return
        legal = p.legal()
        m = self.picked * 1000 + s
        if m not in legal and self.n is not None:
            m = self.castling_to(s) or m             # the king's target g / c for a castling
        if m in legal:
            self.play(m, True)
        else:
            self.status = 'ILLEGAL: CHECK' if m in p.gen(p.sd) else 'ILLEGAL MOVE'
            self.picked = None

    def castling_to(self, s):
        """The castling of the picked king that s means (its rook, or the king's target), or 0."""
        p = self.pos
        if self.n is None or self.picked is None or abs(p.bd[self.picked]) != 6:
            return 0
        for m in p.legal():
            if m // 1000 == self.picked and p.castle_move(m):
                kt, rt = p.targets(m // 1000, m % 1000)
                if s == m % 1000 or (s == kt and self.picked * 1000 + s not in p.legal()):
                    return m
        return 0

    # ---- drawing (the places of CHESS47's PANEL, STATUS, HSHOW, BOARD, FACE, CLOCK) ----
    def to_move(self):
        p = self.pos
        if self.status:
            return self.status
        if self.over:
            return self.over
        if self.prompt is not None:
            return 'CHESS960 No? ' + self.prompt + '_'
        if p.attacked(p.king(p.sd), -p.sd):
            return 'CHECK'
        if self.me == 2:
            return 'WHITE TO MOVE' if p.sd > 0 else 'BLACK TO MOVE'
        if self.human(p.sd):
            return 'YOUR MOVE'
        return 'THINKING ...' if self.me != 0 else 'C47 TO MOVE'

    def screen_xy(self, s):
        f, r = R.file_of(s), R.row_of(s) - 2
        if self.flipped():
            f, r = 7 - f, 7 - r
        return L.BX + L.SQ * f, L.BY + L.SQ * r

    def draw(self):
        pix = set()
        p = self.pos
        bd = p.bd if not self.flipped() else [p.bd[121 - s] if 22 <= s <= 99 else R.OFF for s in range(121)]
        pix |= L.mock(bd)
        for s in (self.picked, self.cursor):
            if s is None:
                continue
            x, y = self.screen_xy(s)
            sq = {(x + j, y + i) for j in range(L.SQ) for i in range(L.SQ)}
            if s == self.picked:                       # the light square's words, inverted (as DRAWSQ)
                pix -= sq
                words_at(pix, x, y, L.square_words(p.bd[s], False), invert=True)
            if s == self.cursor and self.human(p.sd) and not self.over:
                words_at(pix, x, y, [L.FULL, L.FULL] + [L.EDGE] * 20 + [L.FULL, L.FULL])
        for i in range(8):                              # the files (row 10) and the ranks (x 3)
            f = 7 - i if self.flipped() else i
            text(pix, 21 + 24 * i, 10, 'abcdefgh'[f], 10)
            text(pix, 3, 28 + 24 * i, str(f + 1), 10)
        text(pix, 12, 218, 'W %d:%02d  B %d:%02d' % (self.tw // 600, self.tw // 10 % 60, self.tb // 600, self.tb // 10 % 60))
        text(pix, 212, 218, 'CHESS 47')
        if self.level == 0:
            for j, w in enumerate(L.face_words()):
                for i in range(20):
                    if w >> i & 1:
                        pix.add((330 + j, 214 + i))
        who = {1: 'YOU: WHITE', -1: 'YOU: BLACK', 0: 'C47 VS C47', 2: '2 PLAYERS'}[self.me]
        text(pix, 212, 200, who + '   LEVEL ' + LEVELS[self.level], 10)
        if self.n is not None:
            text(pix, 212, 186, 'CHESS960 No %d  %s' % (self.n, C.letters(self.n)), 10)
        text(pix, 212, 156, self.to_move())
        if self.prompt is not None:
            lines = ['TYPE 0-959 AND ENTER', 'ENTER ALONE: RANDOM', '518: NORMAL CHESS', 'ESC: BACK']
        else:
            lines = self.texts[-7:]
        for i, t in enumerate(lines):
            text(pix, 212, 136 - 12 * i, t, 10)
        for y, t in ((45, '8 2 4 6 CURSOR  5 PICK / PLAY'), (34, '+ SWAP SIDES  9 C47 VS C47'),
                     (23, '3 TWO PLAYERS  7 NEW GAME'), (12, '1 LEVEL  / CHESS960  0 END')):
            text(pix, 212, y, t, 10)
        return {(x, y) for x, y in pix if 0 <= x < W and 0 <= y < H}

    # ---- the game kept between runs ----
    def save(self):
        data = {'n': self.n, 'moves': self.moves, 'me': self.me, 'level': self.level, 'tw': self.tw, 'tb': self.tb}
        try:
            with open(SAVE, 'w') as fh:
                json.dump(data, fh)
        except OSError:
            pass

    def load(self):
        try:
            with open(SAVE) as fh:
                data = json.load(fh)
            self.me, self.level = data['me'], data['level']
            self.new(data['n'])
            for m in data['moves']:
                if self.over or m not in self.pos.legal():
                    break
                self.play(m, False)
            self.tw, self.tb = data['tw'], data['tb']
            self.cursor_home()
        except (OSError, ValueError, KeyError, TypeError):
            self.new(None)


def surface(pygame, pix, scale, border=12):
    img = pygame.Surface((W, H))
    img.fill(LCD_BG)
    for x, y in pix:
        img.set_at((x, H - 1 - y), LCD_ON)
    out = pygame.Surface((W * scale + 2 * border, H * scale + 2 * border))
    out.fill(LCD_BG)
    out.blit(pygame.transform.scale(img, (W * scale, H * scale)), (border, border))
    return out


KEYS = {'K_UP': 'UP', 'K_DOWN': 'DOWN', 'K_LEFT': 'LEFT', 'K_RIGHT': 'RIGHT', 'K_RETURN': 'ENTER',
        'K_KP_ENTER': 'ENTER', 'K_SPACE': 'ENTER', 'K_ESCAPE': 'ESC', 'K_BACKSPACE': 'BACK', 'K_KP_PLUS': '+',
        'K_KP_DIVIDE': '/'}


def main():
    ap = argparse.ArgumentParser(description='Chess 47 on the computer, with Chess960')
    ap.add_argument('--scale', type=int, default=3)
    ap.add_argument('--new', action='store_true', help='a new game (else the last one goes on)')
    ap.add_argument('--shot', help='no window: play --keys, then the screen into this PNG')
    ap.add_argument('--keys', default='')
    ap.add_argument('--seed', type=int)
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    if a.shot:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    import pygame
    g = Game()
    if not a.new and not a.shot:
        g.load()
    if a.shot:
        for k in a.keys.split():
            g.press(k)
            while g.c47_turn():
                g.play(g.c47_move(), False)
        pygame.image.save(surface(pygame, g.draw(), a.scale), a.shot)
        print(a.shot, '|', g.to_move(), '|', ' '.join(g.texts[-4:]))
        return
    pygame.display.init()
    keymap = {getattr(pygame, k): v for k, v in KEYS.items()}
    keymap.update({getattr(pygame, 'K_KP%d' % i): str(i) for i in range(10)})
    win = pygame.display.set_mode((W * a.scale + 24, H * a.scale + 24))
    pygame.display.set_caption('Chess 47')
    clock = pygame.time.Clock()
    think_at = None
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                g.save(); pygame.quit(); return
            if e.type == pygame.KEYDOWN:
                k = keymap.get(e.key) or (e.unicode if e.unicode in '0123456789+/' and e.unicode else None)
                if k is None and e.unicode == '=':
                    k = '+'
                if k and g.press(k) == 'quit':
                    g.save(); pygame.quit(); return
        g.tick()
        if g.c47_turn():
            if think_at is None:
                think_at = time.time() + (0.8 if g.me == 0 else 0.4)   # "THINKING ..." seen first
            elif time.time() >= think_at:
                g.play(g.c47_move(), False)
                g.last = time.time()
                think_at = None
        else:
            think_at = None
        win.blit(surface(pygame, g.draw(), a.scale), (0, 0))
        pygame.display.flip()
        clock.tick(20)


if __name__ == '__main__':
    main()
