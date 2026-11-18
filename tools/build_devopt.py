#!/usr/bin/env python3
"""Build the dev-opt files (branch claude/chess47-dev-opt): the test programs of programs_rem/ for the calculator
that the optimisation work needs, as tools/build_chess47.py builds CHESS47 (the macros, the named labels to free local
numbers, STRUCT checked and numbered, the REM lines and the indentation off). They go to build/dev-opt/ (never edited
by hand): NAME.txt (to convert with rejig), NAME_doc.txt (the numbered listing with the comments).
  python3 tools/build_devopt.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_chess47 as B                                       # noqa: E402

PROGRAMS = ('LOCT47',)
OUT = os.path.join(ROOT, 'build', 'dev-opt')


def build(name):
    src = os.path.join(ROOT, 'programs_rem', name + '.txt')
    lines = B.macros([ln.rstrip() for ln in open(src, encoding='utf-8')])
    steps = B.source_steps(lines)
    numeric, num = B.resolve(B.const_steps(steps))
    numeric = B.structures(numeric)
    if [s for s in steps if s.startswith('LBL "')] != ['LBL "%s"' % name] or steps.count('END') != 1:
        raise SystemExit('one program, %s' % name)
    listing, n = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        ind = ln[:len(ln) - len(ln.lstrip())]
        if ln.lstrip().startswith('REM'):
            listing.append('      ' + ind + '; ' + ln.lstrip()[3:].strip())
        else:
            extra = '' if numeric[n] == steps[n] else '    (%s)' % numeric[n].split(' ', 1)[-1]
            listing.append('%4d  %s' % (n + 1, ind + steps[n] + extra))
            n += 1
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(numeric) + '\n')
    with open(os.path.join(OUT, name + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    print('build/dev-opt/%s.txt  %d steps, %d local labels, about %d bytes (.p47, estimated); IF %d, DO %d' % (
        name, len(numeric), sum(1 for s in numeric if re.match(r'LBL \d\d', s)), B.estimate(numeric),
        sum(1 for s in numeric if s.startswith('IF ')), sum(1 for s in numeric if s.startswith('DO '))))
    return numeric


if __name__ == '__main__':
    for nm in sys.argv[1:] or PROGRAMS:
        build(nm)
