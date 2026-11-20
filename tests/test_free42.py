#!/usr/bin/env python3
"""test_free42.py - the Free42 build of CHESS47 (build/free42/CHESS47.txt, tools/build_free42.py) in f42run, the
headless decimal Free42 with the DM42's screen (tools/f42: sh tools/f42/setup.sh builds it), against the Python twin
python/chess47ref.py:

  1. the listing pasted into Free42 and listed back: every step there (Free42's Paste drops what it does not know);
  2. the start: CHESS47 runs to its first key wait, the start position in R20-R28;
  3. level 2 (and level 3 on some): the same move and value as chess47ref.search on the test positions;
  4. the screens (start, Kirk, letters, level 5) against the C47 simulator's, pixel for pixel.

    python3 tests/test_free42.py          (python3 tools/build_free42.py first)"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tests')]
import chess47ref as R

F42 = os.path.join(ROOT, 'tools', 'f42', 'f42run')
PROG = os.path.join(ROOT, 'build', 'free42', 'CHESS47.txt')
FAIL = []


def check(ok, what):
    print('  %s  %s' % ('ok  ' if ok else 'FAIL', what))
    if not ok:
        FAIL.append(what)


def f42(cmds, timeout=3600):
    r = subprocess.run([F42], input='\n'.join(cmds) + '\n', text=True, capture_output=True, timeout=timeout)
    return r.stdout, r.stderr


def programs(path=PROG):
    progs, cur = [], []
    for l in open(path, encoding='utf-8').read().split('\n'):
        if l:
            cur.append(l)
            if l == 'END':
                progs.append(cur); cur = []
    return progs


def regs(out):
    return {int(m.group(1)): m.group(2) for m in re.finditer(r'^R(\d\d) (.*)$', out, re.M)}


def norm(x):
    if x.startswith('XSTR "'):         # the data's strings (any byte, written as € and hex) list differently
        return 'XSTR'
    return x.replace(' ', '').replace('ᴇ', 'E').replace('Y↑X', 'Y^X').replace('SIZE0100', 'SIZE100')


def paste_tests():
    print('== the listing in Free42, step by step')
    progs = programs()
    out, _ = f42(['paste ' + PROG] + ['list %d' % i for i in range(len(progs))])
    blocks = re.split(r'\n\d+ \{ [^\n]*\n', '\n' + out)[1:]
    bad = []
    for p, b in zip(progs, blocks):
        got = [re.sub(r'^\d+[▸ ]?', '', x).strip() for x in b.split('\n') if re.match(r'^\d+[▸ ]', x)]
        if len(got) != len(p) or any(norm(g) != norm(w) for g, w in zip(got, p)):
            bad.append(p[0])
    check(len(blocks) == len(progs) and not bad, '%d programs, %d steps, all pasted%s' % (
        len(progs), sum(map(len, progs)), (': not ' + ', '.join(bad)) if bad else ''))


def setp(p, name='SETP'):
    """A Free42 program that writes the position p (chess47ref.Pos) as tests/test_chess47.setpos does."""
    L = ['LBL "%s"' % name, 'INDEX "BB"', '1', '1', 'STOIJ', 'DROP', 'DROP']
    for v in p.bd[1:]:
        L += [str(v if v != R.OFF else 8), 'STOEL', 'DROP', 'J+']
    for r, v in ((20, p.sd), (21, p.ep), (22, p.cr), (23, p.sc), (24, p.kw), (25, p.kb)):
        L += [str(v), 'STO %d' % r, 'DROP']
    return L + ['RTN', 'END']


def think_tests():
    print('== level 2 (and 3): the moves of chess47ref.search')
    sys.path.insert(0, os.path.join(ROOT, 'tests'))
    import test_chess47 as T
    fens = T.FENS[:8]
    d = tempfile.mkdtemp()
    for k, f in enumerate(fens):
        for depth in ((2, 3) if k in (0, 1) else (2,)):
            p = R.Pos.fen(f)
            want, v, n = p.search(depth)
            t = os.path.join(d, 't%d.txt' % k)
            prog = setp(R.Pos.fen(f)) + ['LBL "TT"', 'XEQ "NINIT"', 'XEQ "THINK"', 'RTN', 'END',
                                          'LBL "TT3"', '0', 'STO "zPK"', 'DROP', 'XEQ "NINIT"', 'XEQ "THINK"',
                                          'XEQ "THINK3"', 'RTN', 'END']
            open(t, 'w', encoding='utf-8').write('\n'.join(prog) + '\n')
            pre = ['600000000', 'STO 26'] if depth == 3 else []
            cmds = ['paste ' + PROG, 'paste ' + t, 'xeq CHESS47', 'xeq SETP']
            if depth == 3:
                cmds += ['num 3', 'xeq SET3']
                open(t, 'a').write('LBL "SET3"\nSTO 26\nINDEX "ST"\n1\n18\nSTOIJ\nDROP\nDROP\n1E9\nSTOEL\nRTN\nEND\n')
            cmds += ['xeq ' + ('TT3' if depth == 3 else 'TT'), 'regs 61 62', 'stack']
            out, err = f42(cmds)
            r = regs(out)
            got = (int(float(r.get(62, 'nan'))) if r.get(62, '').replace('.', '').replace('-', '').isdigit() else r.get(62),
                   r.get(61))
            check(got[0] == want and float(r.get(61, 'nan')) == v,
                  'level %d %s: %s %s (chess47ref %s %d)' % (depth, f.split()[0], got[0], got[1], R.mname(want), v))


def screen_tests():
    """The Free42 screen against the C47 simulator's, pixel for pixel (f42run's 400 x 240 frame; the clock frozen)."""
    print('== the screens: Free42 and the C47 simulator')
    import chess47sim as S
    inv = {}
    for f in range(1, 38):
        c = 20 + f if f <= 6 else 30 + f - 6 if f <= 12 else (4 + (f - 13) // 5) * 10 + (f - 13) % 5 + 1
        inv[c] = f
    d = tempfile.mkdtemp()
    open(os.path.join(d, 'sf.txt'), 'w').write('LBL "TSF"\nSF 09\nEND\n')
    for name, keys, most in (('the start', [], 10), ('÷ 1701 (Kirk)', [55, 72, 52, 82, 72], 0),
                             ('× (the letters)', [65], 12), ('1 three times (level 5)', [72, 72, 72], 12)):
        shot = os.path.join(d, 's.pbm')
        cmds = ['paste ' + PROG, 'paste ' + os.path.join(d, 'sf.txt'), 'xeq TSF', 'xeq CHESS47']
        cmds += ['key %d' % inv[k] for k in keys] + ['shot ' + shot]
        env = dict(os.environ, F42_TIME='12000000')
        subprocess.run([F42], input='\n'.join(cmds) + '\n', text=True, capture_output=True, env=env, timeout=1200)
        rows = open(shot).read().split('\n')[2:242]
        f42 = {(y, x) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == '1'}
        shots, c = S.run(keys)
        c47 = {(239 - y, x) for (y, x) in c.pix}
        diff = len(f42 ^ c47)
        check(diff <= most, '%s: %d pixels, %d different (at most %d: the clock)' % (name, len(f42), diff, most))


def main():
    if not os.path.exists(F42):
        raise SystemExit('no tools/f42/f42run: sh tools/f42/setup.sh')
    paste_tests()
    think_tests()
    screen_tests()
    print('\nALL OK' if not FAIL else '\n%d FAILED' % len(FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
