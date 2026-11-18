#!/usr/bin/env python3
"""Build the CHESS47 files from the commented source programs_rem/CHESS47.txt (as Logic 47, Zones 47, Elements 47):
the markers REM ==== GLYPHS and FACE (python/layout.py), BOOK and BOOKN (python/book.py) filled, the macros
(DEF :NAME: ... ENDDEF, written out where USE :NAME: stands) and the constants @NAME (the rows of BD, python/layout.py BD)
filled, named labels LBL :NAME: get free local numbers, the STRUCT
commands are checked as the firmware's VALID does and numbered (255 a program: C47, R47, DM42n), the REM lines and the indentation go.
Files: programs/CHESS47.txt, build/CHESS47.txt (the calculator file, to convert with rejig),
listings/CHESS47_doc.txt (numbered steps with comments), listings/CHESS47_labels.txt.
  python3 tools/build_chess47.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'CHESS47'
NAMED_RE = re.compile(r'(LBL|GTO|XEQ) :([A-Za-z0-9?]{1,7}):$')
OPENERS = {'IF': 'ENDIF', 'DO': 'ENDDO', 'REPEAT': 'UNTIL'}
STRUCT = ('IF', 'ELSE', 'ENDIF', 'DO', 'WHILE', 'ENDDO', 'REPEAT', 'UNTIL')
DM42_MAX = 255                 # the C47 / R47 / DM42n (CHESS47 needs more than the old DM42's 10)
C47_LEVELS = 63
NOT_USED = ('FOR', 'NEXT', 'FORₓ', 'NEXTₓ', 'FOR𝑦ˣ', 'FORᵀᴼᴾ')


def is_test(step):
    """A step that leaves a test answer (the firmware's structTest list: the comparisons, the flag and type
    tests ending with ?, the counters, KEY?)."""
    op = step.split(' ')[0]
    return op.endswith('?') or op in ('DSE', 'ISG', 'DSZ', 'ISZ', 'DSL', 'ISE')


def structures(steps):
    """The steps with the partner numbers of the STRUCT commands, as VALID numbers them (manage.c /
    structured.c structWalkProgram): per program, IF, DO and REPEAT in three series from 1, in the order
    the openers appear; ELSE, WHILE, ENDDO, ENDIF, UNTIL take the number of their opener. Stops on what
    VALID refuses (a closer without its opener or of another kind, a structure left open at END or across
    a routine (RTN then LBL), a DO without WHILE, an IF / WHILE / UNTIL without a test just before it) and
    on a test before ELSE, ENDIF, DO, ENDDO, REPEAT or UNTIL: the firmware never skips those (structured.c
    structNoLegacySkip)."""
    out, open_, n = [], [], {}

    def fail(i, msg):
        raise SystemExit('STRUCT, step %d (%s): %s' % (i + 1, steps[i], msg))
    for i, s in enumerate(steps):
        op = s.split(' ')[0]
        prev = steps[i - 1] if i else ''
        if op in NOT_USED:
            fail(i, 'FOR / NEXT not used here (they take the start, end and step off the stack)')
        if op in STRUCT and s != op:
            fail(i, 'written without a number: the build numbers the structures')
        if op in ('IF', 'WHILE', 'UNTIL') and not is_test(prev):
            fail(i, 'no test just before it')
        if op in ('ELSE', 'ENDIF', 'DO', 'ENDDO', 'REPEAT', 'UNTIL') and is_test(prev) and not op == 'UNTIL':
            fail(i, 'a test before it: the firmware never skips a structure step')
        if s == 'END' or (s.startswith('LBL ') and prev == 'RTN'):
            if open_:
                fail(i, 'structure %s %02d still open' % tuple(open_[-1][:2]))
            if s == 'END':
                n = {}
        if op in OPENERS:
            n[op] = n.get(op, 0) + 1
            # the original DM42 (c43 structured.h, OLD_HW): 10 numbers of each kind per program, 10 levels
            if n[op] > DM42_MAX or len(open_) >= C47_LEVELS:
                fail(i, 'past the C47 limit: %d %s a program, %d levels (structured.h)' % (DM42_MAX, op, C47_LEVELS))
            open_.append([op, n[op], False])
            out.append('%s %02d' % (op, n[op]))
            continue
        if op in STRUCT:
            want = {'ELSE': 'IF', 'ENDIF': 'IF', 'WHILE': 'DO', 'ENDDO': 'DO', 'UNTIL': 'REPEAT'}[op]
            if not open_ or open_[-1][0] != want:
                fail(i, 'no %s open here' % want)
            top = open_[-1]
            if op in ('ELSE', 'WHILE'):
                if top[2]:
                    fail(i, 'a second %s' % op)
                top[2] = True
            if op == 'ENDDO' and not top[2]:
                fail(i, 'a DO without WHILE')
            if op in ('ENDIF', 'ENDDO', 'UNTIL'):
                open_.pop()
            out.append('%s %02d' % (op, top[1]))
            continue
        out.append(s)
    if open_:
        raise SystemExit('STRUCT: %s %02d still open at the end' % tuple(open_[-1][:2]))
    return out


def estimate(steps):
    """Estimated .p47 bytes of a program: 2.3 bytes per command, 2 + its characters per number and
    per binary number, 2 + its UTF-8 bytes per text. Calibrated on Almanac 47's MOON47 (4 836 bytes) and
    NAVFULL (24 160 bytes), within 3 % of both; rejig gives the real size."""
    b = 0.0
    for s in steps:
        if s.startswith('"'):
            b += 2 + len(s.encode('utf-8')) - 2
        elif re.fullmatch(r'-?[\d.]+(E-?\d+)?|[01]+#2', s):
            b += 2 + len(s)
        elif NAMED_RE.match(s):
            b += 3 + len(s.split(':')[1])      # command, 249, length, the name (bytes of the test program)
        else:
            b += 2.3
    return int(round(b))


def resolve(steps):
    """The steps with each named label replaced by a free local number (the fallback file), and the
    numbers: the numbers 00-99 not taken by a numeric label of the first program (the other programs
    have their own local labels), in order. Stops on a name defined twice, a name used but not defined,
    more labels than 00-99."""
    defs = [m.group(2) for s in steps for m in [NAMED_RE.match(s)] if m and m.group(1) == 'LBL']
    dup = sorted({d for d in defs if defs.count(d) > 1})
    if dup:
        raise SystemExit('named labels defined twice: %s' % ', '.join(dup))
    used = {m.group(2) for s in steps for m in [NAMED_RE.match(s)] if m}
    if used - set(defs):
        raise SystemExit('named labels used but not defined: %s' % ', '.join(sorted(used - set(defs))))
    bad = [s for s in steps if re.match(r'(LBL|GTO|XEQ) :', s) and not NAMED_RE.match(s)]
    if bad:
        raise SystemExit('a named label is 1-7 letters or digits between colons: %s' % bad[:3])
    first = steps[:steps.index('END') + 1] if 'END' in steps else steps
    taken = {int(m.group(1)) for s in first for m in [re.fullmatch(r'LBL (\d\d)', s)] if m}
    free = [n for n in range(100) if n not in taken]
    if len(defs) > len(free):
        raise SystemExit('%d named labels, only %d local numbers free' % (len(defs), len(free)))
    num = dict(zip(defs, free))
    return [NAMED_RE.sub(lambda m: '%s %02d' % (m.group(1), num[m.group(2)]), s) for s in steps], num


def programs(steps):
    """The programs of a list of steps (each ends with END)."""
    out, cur = [], []
    for s in steps:
        cur.append(s)
        if s == 'END':
            out.append(cur); cur = []
    return out


def source_steps(lines):
    """The steps of the source lines: no REM, no empty lines, the indentation off."""
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith('REM')]


def fill(lines):
    """The marker line REM ==== GLYPHS replaced by the glyph words of python/layout.py."""
    sys.path.insert(0, os.path.join(ROOT, 'python'))
    import layout
    out = []
    for ln in lines:
        if ln.strip() == 'REM ==== GLYPHS':
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(ind + 'REM the glyph words O S M of python/layout.py (written by the build)')
            out += [ind + st for st in layout.glyph_steps()]
        elif ln.strip() == 'REM ==== BOOK':
            import book
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(ind + 'REM the opening book of python/book.py: the matrix OB (written by the build)')
            out += [ind + st for st in book.steps()]
        elif ln.strip() == 'REM ==== BOOKN':
            import book
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(ind + 'REM the rows of OB (written by the build)')
            out.append(ind + str(len(book.LINES)))
        elif ln.strip() == 'REM ==== KNIGHTS':
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(ind + 'REM the knights\' masks of python/layout.py into row 21 of BD (written by the build)')
            out += [ind + st for st in layout.knight_steps()]
        elif ln.strip() == 'REM ==== FACE':
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(ind + 'REM the face of python/layout.py, one column a word (written by the build)')
            out += [ind + st for st in layout.face_steps()]
        else:
            out.append(ln)
    return out


CONST_RE = re.compile(r'@([A-Z]+)$')               # (the names of MATS + R / C: their sizes)
MACRO_RE = re.compile(r'(DEF|USE) :([A-Za-z0-9]{1,7}):$')


def macros(lines):
    """The macros: a block DEF :NAME: ... ENDDEF (its REM lines kept as comments) is taken out of the source and
    written out, with the indentation of the line, where USE :NAME: stands (a REM line marks it in the listing).
    A macro keeps the steps the same in every place it is used (the engine's inner loops are inlined for speed)."""
    defs, out, cur = {}, [], None
    for ln in lines:
        st = ln.strip()
        m = MACRO_RE.match(st)
        if m and m.group(1) == 'DEF':
            if cur is not None:
                raise SystemExit('DEF :%s: inside DEF :%s:' % (m.group(2), cur))
            cur = m.group(2)
            if cur in defs:
                raise SystemExit('macro :%s: defined twice' % cur)
            defs[cur] = []
        elif st == 'ENDDEF':
            if cur is None:
                raise SystemExit('ENDDEF without DEF')
            cur = None
        elif cur is not None:
            defs[cur].append(st)
        else:
            out.append(ln)
    if cur is not None:
        raise SystemExit('DEF :%s: without ENDDEF' % cur)
    res = []
    for ln in out:
        m = MACRO_RE.match(ln.strip())
        if m:
            if m.group(2) not in defs:
                raise SystemExit('USE of the macro :%s:, not defined' % m.group(2))
            ind = ln[:len(ln) - len(ln.lstrip())]
            res.append(ind + 'REM (macro :%s:)' % m.group(2))
            res += [ind + b for b in defs[m.group(2)]]
        else:
            res.append(ln)
    return res


NUMBER = 16                    # bytes a number of a real matrix (an estimate: real34, to be checked with MEM#)


def constants():
    """The constants @NAME: the rows and offsets of the game's matrices (python/layout.py BD), @XR @XC the sizes of
    the matrix X (layout.MATS); MEM the bytes the start checks with MEM# (the game's matrices, GL, OB at NUMBER bytes a
    number, 3 000 to spare, up to the thousand), GHM the game record GH's."""
    sys.path.insert(0, os.path.join(ROOT, 'python'))
    import layout, book
    c = {k: str(v) for k, v in layout.BD.items()}
    for k, (r, n) in layout.MATS.items():
        c[k + 'R'], c[k + 'C'] = str(r), str(n)
    els = sum(r * n for r, n in layout.MATS.values())
    need = (els + layout.GL_SIZE + book.ob_size()) * NUMBER + 3000
    c['MEM'] = str(-(-need // 1000) * 1000)
    c['GHM'] = str(layout.GH_SIZE * NUMBER)
    return c


def const_steps(steps):
    """The steps with each constant @NAME replaced by its number."""
    c = constants()
    bad = sorted({s for s in steps if CONST_RE.match(s) and s[1:] not in c})
    if bad:
        raise SystemExit('constants not defined: %s' % ', '.join(bad))
    return [c[s[1:]] if CONST_RE.match(s) else s for s in steps]


def labels_text(lines, num):
    out = ['CHESS47 local labels: name (programs_rem/CHESS47.txt), number (build/CHESS47.txt), what it does', '']
    for i, ln in enumerate(lines):
        m = NAMED_RE.match(ln)
        if m and m.group(1) == 'LBL':
            j = i
            while j > 0 and lines[j - 1].startswith('REM'):
                j -= 1
            note = lines[j][3:].strip(' -') if j < i else ''
            note = re.sub(r'^(LBL )?:%s:\s*' % m.group(2), '', note)
            out.append(':%s:%s %02d  %s' % (m.group(2), ' ' * (8 - len(m.group(2))), num[m.group(2)], note[:90]))
    return '\n'.join(out) + '\n'


def build():
    src = os.path.join(ROOT, 'programs_rem', NAME + '.txt')
    lines = macros(fill([ln.rstrip() for ln in open(src, encoding='utf-8')]))
    steps = source_steps(lines)
    numeric, num = resolve(const_steps(steps))
    numeric = structures(numeric)
    if [s for s in steps if s.startswith('LBL "')] != ['LBL "%s"' % NAME] or steps.count('END') != 1:
        raise SystemExit('one program, %s' % NAME)
    listing, n = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        ind = ln[:len(ln) - len(ln.lstrip())]
        if ln.lstrip().startswith('REM'):
            listing.append('      ' + ind + '; ' + ln.lstrip()[3:].strip())
        else:
            extra = '' if numeric[n] == steps[n] else '    (%s)' % (
                numeric[n] if CONST_RE.match(steps[n]) else numeric[n].split(' ', 1)[1])
            listing.append('%4d  %s' % (n + 1, ind + steps[n] + extra))
            n += 1
    for d in ('programs', 'build', 'listings'):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    for d in ('programs', 'build'):
        with open(os.path.join(ROOT, d, NAME + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(numeric) + '\n')
    with open(os.path.join(ROOT, 'listings', NAME + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    with open(os.path.join(ROOT, 'listings', NAME + '_labels.txt'), 'w', encoding='utf-8') as fh:
        fh.write(labels_text(lines, num))
    return numeric


if __name__ == '__main__':
    st = build()
    txt = [s for s in st if s.startswith('"')]
    print('%s %5d steps, %2d local labels, about %d bytes (.p47, estimated); IF %d, DO %d' % (
        NAME, len(st), sum(1 for s in st if re.match(r'LBL \d\d', s)), estimate(st),
        sum(1 for s in st if s.startswith('IF ')), sum(1 for s in st if s.startswith('DO '))))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_forum
    build_forum.build(NAME)                                   # build/forum/CHESS47.p47u, the commented rejig source
