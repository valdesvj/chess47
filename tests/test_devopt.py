#!/usr/bin/env python3
"""The dev-opt test programs in the simulator (python/c47sim.py, which keeps local registers per subroutine level as
the firmware does): LOCT47 runs its five timings and shows them, and after the key its XEQ'd routine cannot read the
caller's R.05 (the firmware: local register .05 not defined).
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
    check(c.steps > 6 * 10000, 'the five timings and the empty loop ran (%d steps), TM deleted: %s' % (c.steps, 'TM' not in c.mats))
    check(err is not None and 'no local register' in err,
          'the XEQ\'d routine cannot read R.05 of LOCT47 (as the firmware): %s' % err)
    print('\n%s' % ('ALL OK' if not FAIL else '%d FAILED' % len(FAIL)))
    return not FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
