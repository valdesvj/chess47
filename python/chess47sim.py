"""chess47sim.py - run build/CHESS47.txt in the C47 simulator (c47sim.py, from Almanac 47 via Logic 47: the bitwise
commands) and turn its screens into pictures.
  run(keys)        the screens shown while CHESS47 waits for a key, and the simulator (its registers, matrices)
  board(c)         the board of the matrix BD as a list bd[0..120] (as chess47ref.Pos.bd)
  png(fn, pix)     a PNG of one screen (LCD colours, 3 pixels per C47 pixel)
  python3 python/chess47sim.py   writes the screens in docs/ and prints the step counts"""
import os, struct, sys, zlib
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import c47sim

PROG = os.environ.get('CHESS47_PROG') or os.path.join(ROOT, 'build', 'CHESS47.txt')
W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)
UP, DOWN, LEFT, RIGHT, PICK, HAND, LEVEL, END, NEW, AUTO = 53, 73, 62, 64, 63, 85, 72, 82, 52, 54
STEP_MS = 0.17                                   # ms a step on the C47 (Almanac 47's measure)


def run(ks, prog=PROG, stack=None, regs=None, maxsteps=10 ** 9, mats=None):
    """ks: the keys (None: no key at that KEY?); regs, mats: variables kept from an earlier run (the saved game)"""
    c = c47sim.load([prog])
    c.s = [D(v) for v in (stack or (0, 0, 0, 0))]; c.pix = []; c.keys = list(ks); c.steps = 0
    c.at_steps = []
    if regs:
        c.reg.update(regs)
    if mats:
        c.mats.update(mats)

    class F(list):
        def append(self, f): c.at_steps.append(c.steps); super().append(f)
    c.frames = F()
    try:
        c.run('CHESS47', maxsteps=maxsteps)
        c.ended = True
    except StopIteration:
        c.ended = False
    shots = [{(x, H - 1 - y) for y, x in f if 0 <= y < H and 0 <= x < W} for f in c.frames]
    return shots, c


def board(c):
    m = c.mats['BD'][0]
    return [None] + [int(v) if float(v) == int(float(v)) else float(v) for v in m]


def png(fn, pix, scale=3, border=12):
    w, h = W * scale + 2 * border, H * scale + 2 * border
    buf = bytearray(bytes(LCD_BG) * (w * h))
    dot = bytes(LCD_ON) * scale
    for x, r in pix:
        for dy in range(scale):
            o = ((border + r * scale + dy) * w + border + x * scale) * 3
            buf[o:o + len(dot)] = dot
    raw = b''.join(b'\x00' + bytes(buf[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(fn, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                 + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def secs(steps):
    return steps * STEP_MS / 1000.0


if __name__ == '__main__':
    import time
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    t = time.time()
    shots, c = run([])
    print('start: %d steps (%.1f s on the C47), %.1f s here' % (c.steps, secs(c.steps), time.time() - t))
    png(os.path.join(ROOT, 'docs', 'CHESS47_start.png'), shots[-1])
    # your move e2-e4 (5 8 8 5), the C47's reply; then g1 picked (the square inverted)
    keys = [PICK, UP, UP, PICK, DOWN, DOWN, DOWN, RIGHT, RIGHT, PICK]
    shots, c = run(keys)
    png(os.path.join(ROOT, 'docs', 'CHESS47_play.png'), shots[-1])
    print('docs/CHESS47_play.png: e2-e4, the C47 %s, g1 picked; the reply %.0f s on the C47'
          % (c.reg.get('79'), secs(c.at_steps[4] - c.at_steps[3])))
    shots, c = run([HAND] * 8)
    png(os.path.join(ROOT, 'docs', 'CHESS47_game.png'), shots[-1])
    print('docs/CHESS47_game.png: the C47 against itself, 8 moves')
