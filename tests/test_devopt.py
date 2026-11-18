#!/usr/bin/env python3
"""The dev-opt test programs in the simulator (python/c47sim.py): LOCT47 v0.2 runs its ten timings of the matrix
commands, shows them and ends (TM and TS deleted). (v0.1's subroutine test, on the C47: "Out of range".)
  python3 tools/build_devopt.py && python3 tests/test_devopt.py"""
import os, sys
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import c47sim                                                    # noqa: E402
import build_devopt                                              # noqa: E402

FAIL = []


def check(ok, what):
    print('  %s  %s' % ('ok  ' if ok else 'FAIL', what))
    if not ok:
        FAIL.append(what)


def main():
    print('== LOCT47 (build/dev-opt/LOCT47.txt)')
    st = build_devopt.build('LOCT47')
    fn = os.path.join(build_devopt.OUT, 'LOCT47.txt')
    check(open(fn, encoding='utf-8').read().split('\n')[:-1] == st, 'build/dev-opt/LOCT47.txt is the build of programs_rem/LOCT47.txt')
    c = c47sim.load([fn])
    c.s = [D(1), D(2), D(3), D(4)]; c.pix = []; c.keys = [None, 63]; c.steps = 0
    c.frames = []
    err = None
    try:
        c.run('LOCT47', maxsteps=10 ** 7)
    except StopIteration:
        err = 'waits for a key'
    except ValueError as e:
        err = str(e)
    check(err is None or err == 'waits for a key', 'LOCT47 v0.2 runs to its end in the simulator (%s)' % (err or 'ended'))
    check(c.steps > 11 * 2000 * 2, 'the ten tests and the empty loop ran (%d steps)' % c.steps)
    check('TM' not in c.mats and 'TS' not in c.mats, 'the matrices TM and TS deleted')
    print('\n%s' % ('ALL OK' if not FAIL else '%d FAILED' % len(FAIL)))
    return not FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
