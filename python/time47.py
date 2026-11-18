"""time47.py - CHESS47's time on the C47 estimated from the simulator, with the costs measured on Victor's DM42n
(LOCT47 v0.1 and v0.2, Nov 18, 2026; docs/DEVOPT.md), not the simulator's equal steps.

The firmware copies the whole indexed matrix into a new one at every element command (matrix.c callByIndexedMatrix)
and copies it back when the command says it changed something: STOEL, STOSEQ and STOIJ (store.c storeIjReal returns
true) and J+ at the end of a row. So their cost grows with the matrix's elements n:
  read  (RCLEL, J+): 550 us at n = 120, 5 000 at 1 680, 6 100 at 2 760 (measured), linear between, 450 at n = 1
  write (STOEL, STOIJ): 800, 7 950, 12 900 (measured), 650 at n = 1
  RCLSEQ = read + read (RCLEL then J+), STOSEQ = write + read; INDEX 175
  XEQ 400 + RTN 270 (670 measured together); any other step 120 (RCL R.05 110, RCL IND 120-130).
The seconds are an estimate (the clock of the DM42n changes with USB power or battery: the empty loop was 360 us in
one run and 200 in the other); compare two versions with the same model.
  est = Estimator(c); c.count = est.hook; c.run(...); est.us"""
import bisect

READ = [(1, 450), (120, 550), (1680, 5000), (2760, 6100)]
WRITE = [(1, 650), (120, 800), (1680, 7950), (2760, 12900)]
PLAIN, INDEX, XEQ, RTN = 120, 175, 400, 270


def interp(pts, n):
    xs = [p[0] for p in pts]
    i = min(max(bisect.bisect_left(xs, n), 1), len(pts) - 1)
    (x0, y0), (x1, y1) = pts[i - 1], pts[i]
    return y0 + (y1 - y0) * (n - x0) / (x1 - x0)


class Estimator:
    def __init__(self, c):
        self.c = c
        self.us = 0.0
        self.by = {}

    def size(self):
        m = self.c.mats.get(self.c.cur)
        return len(m) * len(m[0]) if m else 1

    def add(self, what, us):
        self.us += us
        self.by[what] = self.by.get(what, 0) + us

    def hook(self, op, x):
        if op in ('RCLEL', 'J+', 'I+'):
            self.add(op, interp(READ, self.size()))
        elif op in ('STOEL', 'STOIJ'):
            self.add(op, interp(WRITE, self.size()))
        elif op == 'RCLSEQ':
            self.add(op, 2 * interp(READ, self.size()))
        elif op == 'STOSEQ':
            self.add(op, interp(WRITE, self.size()) + interp(READ, self.size()))
        elif op == 'INDEX':
            self.add(op, INDEX)
        elif op in ('XEQ', 'GSB'):
            self.add('XEQ', XEQ)
        elif op == 'RTN':
            self.add('RTN', RTN)
        else:
            self.add('other', PLAIN)
