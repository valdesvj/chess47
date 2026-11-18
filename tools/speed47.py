"""speed47.py - level 3's answers a second on the C47 (python/time47.py's model of Victor's DM42n), the program run in
the simulator to the end on some positions; the level-2 search first is taken off. tools/elo47.py's budgets for
levels 3, 4, 5 (60 s, 3 min, 9 min) are these answers a second times the seconds. v0.8.1: 12.7 (a position where
the level-3 part comes out at 0 s is left out of the sum).
    python3 tools/speed47.py      (about 30 minutes)"""
import copy, os, sys
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'tests')]
import chess47ref as R, chess47sim as S, time47, test_chess47 as T
prog = T.test_copy()
fens = [T.FENS[0], T.FENS[1], T.FENS[7], T.FENS[8],
        'r1b1kb1r/2p1pppp/2Q5/p3N3/2PPpn2/P6P/1P3PP1/RN2K2R b KQkq - 0 12',
        'r2q1rk1/pp2bppp/2n1bn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQ1RK1 w - - 0 9',
        '2r2rk1/pp1q1ppp/2n1pn2/3p4/3P4/2NBPN2/PPQ2PPP/2R2RK1 w - - 0 14']
tot_n = tot_s = 0
for f in fens:
    p = R.Pos.fen(f)
    shots, c = S.run([], prog=prog)
    T.setpos(c, p)
    c.reg['26'] = D(3)
    c.mats['ST'][0][17] = D(10 ** 9)
    est = time47.Estimator(c); c.count = est.hook
    c.run('TTH3', maxsteps=10 ** 10)
    q = copy.deepcopy(p); m, v, n = q.search(3)
    shots, c2 = S.run([], prog=prog)
    T.setpos(c2, p); c2.reg['26'] = D(2)
    e2 = time47.Estimator(c2); c2.count = e2.hook
    c2.run('TTHK', maxsteps=10 ** 10)
    s = (est.us - e2.us) / 1e6
    print('   level 2 %.1f s, level 3 to the end %.0f s' % (e2.us / 1e6, est.us / 1e6))
    if s > 1:
        tot_n += n; tot_s += s
    print('%-60s answers %6d  %6.0f s  %5.1f a/s  ok %s' % (f[:60], n, s, n / s, (int(c.reg['62']), int(c.reg['61'])) == (m, v)), flush=True)
print('all: %.2f answers a second' % (tot_n / tot_s))
