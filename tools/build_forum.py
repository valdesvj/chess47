#!/usr/bin/env python3
"""build_forum.py - the commented rejig source (.p47u) of CHESS47, for the forum and the PROGRAMS folder of a C47
release (as Almanac 47's and Zones 47's tools/build_forum.py: '@' header lines, then the steps).

  build/forum/CHESS47.p47u  from build/CHESS47.txt (the steps) and listings/CHESS47_doc.txt (the comments)

The steps are those of build/*.txt, one by one (the same .p47 as the plain listing): indented as the source
(STRUCT, two spaces a level), the partner numbers written (DO 01 ... ENDDO 01). The comments of the source
(its REM lines) go after ';' at the end of the steps they stand before, one comment line a step, in a column;
the name of a label (LBL :INIT:) is given as a comment on its LBL and on each XEQ / GTO to it. rejig drops
everything after ';', so the comments take no memory. A line that starts with ';' or '#' would become a REM
step on the calculator (Almanac 47 DEVELOPMENT_NOTES): there are none; the source's header is in '@' lines.

  python3 tools/build_chess47.py   (writes it too)
  rejig: the .p47 of build/forum/CHESS47.p47u must be the size of the one of build/CHESS47.txt.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'forum')
AUTHOR = 'Victor Valdes'
SOURCE = 'https://github.com/valdesvj/chess47'
COL = 32                              # the column of the ';' comments (wider steps: two spaces after them)

HEAD = {
    'CHESS47': """@ Index:   Chess against the C47: legal moves, check, mate, draws, a 2-ply search, a book, a clock
@ Author:  %(author)s
@ Version: %(version)s
@ Source:  %(source)s
@ Tested:  C47 simulator only (python/c47sim.py): tests/test_chess47.py, the moves, the scores and the choices of
@ Tested:  the search against python/chess47ref.py (the same algorithm), whose move generator gives the published
@ Tested:  perft counts; 10 matches against a python-chess player (tools/match47.py); not yet run on a calculator
@ Input:   none: XEQ 'CHESS47', then the keys
@ Output:  the board; at 0 your stack and LASTx as before
@
""",
}

STEP = re.compile(r'^\s*(\d+)  (.*)$')
NAMED = re.compile(r'^(\s*)(.*?)\s{4}\((\d+)\)$')            # "XEQ :INIT:    (83)", "DO    (01)"


def parse(name):
    """The doc listing: the header comments, then [(indent, step text with names, number, comments before it)]."""
    head, steps, pending = [], [], []
    for ln in open(os.path.join(ROOT, 'listings', name + '_doc.txt'), encoding='utf-8'):
        ln = ln.rstrip('\n')
        m = STEP.match(ln)
        if m:
            body = m.group(2)
            ind = body[:len(body) - len(body.lstrip())]
            steps.append((ind, body.strip(), int(m.group(1)), pending)); pending = []
        elif ln.strip().startswith(';'):
            text = ln.strip()[1:].strip()
            (pending if steps else head).append(text)          # before step 1: the program's header
    return head, steps


def data_notes(name, plain, names):
    """Notes on numbered labels with no name (none in CHESS47; kept from Logic 47)."""
    return {}


def build(name):
    head, steps = parse(name)
    plain = open(os.path.join(ROOT, 'build', name + '.txt'), encoding='utf-8').read().split('\n')
    plain = [s for s in plain if s.strip()]
    if len(plain) != len(steps):
        raise SystemExit('%s: %d steps in build/, %d in listings/' % (name, len(plain), len(steps)))
    m = re.search(r'v(\d+\.\d+\.\d+)', head[0])
    version = m.group(1) if m else '?'
    names = {}                                                    # label number -> :NAME:
    for ind, text, n, com in steps:
        mm = NAMED.match(ind + text)
        if mm and mm.group(2).startswith('LBL :'):
            names[mm.group(3)] = mm.group(2)[4:]
    out = [(HEAD[name] % dict(author=AUTHOR, version=version, source=SOURCE)).rstrip('\n')]
    data = data_notes(name, plain, names)
    out += ['@ ' + h if h else '@' for h in head] + ['@', '']
    queue, last = [], None
    for k, ((ind, text, n, com), step) in enumerate(zip(steps, plain)):
        if ';' in step or step.lstrip().startswith(('#', '@')):
            raise SystemExit('%s step %d: %r would not survive rejig' % (name, n, step))
        if com:
            if queue and last is not None:                       # the rest of the last block: on its last step
                out[last] += ' ' + ' '.join(queue)
            queue = list(com)
        note = ''
        mm = re.fullmatch(r'(LBL|XEQ|GTO) (\d\d)', step)
        if mm and mm.group(2) in names:
            note = names[mm.group(2)] if mm.group(1) == 'LBL' else '-> ' + names[mm.group(2)]
        if k in data:
            note = (note + '  ' if note else '') + data[k]
        c = queue.pop(0) if queue else ''
        if note and c:
            c = note + '  ' + c
        elif note:
            c = note
        line = ind + step
        if c:
            line = line.ljust(COL) + '; ' + c if len(line) < COL else line + '  ; ' + c
        out.append(line)
        if c:
            last = len(out) - 1
    if queue and last is not None:
        out[last] += ' ' + ' '.join(queue)
    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, name + '.p47u')
    with open(fn, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out).rstrip('\n') + '\n')
    ncom = sum(1 for ln in out if re.search(r'\s; ', ln))
    print('build/forum/%s.p47u  %d steps, %d with a comment, version %s' % (name, len(plain), ncom, version))
    return out


if __name__ == '__main__':
    for nm in sys.argv[1:] or ('CHESS47',):
        build(nm)
