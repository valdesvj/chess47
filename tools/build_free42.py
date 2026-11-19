#!/usr/bin/env python3
"""build_free42.py - CHESS47 for Free42 on the SwissMicros DM42 / DM42n (stock firmware, Free42 3.3), converted
from the C47 program (build/f42/CHESS47.txt: the drawn pieces, with the REM ==== IF F42 sections of the source), step for step where Free42 can do the same:

  routines     every C47 local label (LBL :NAME:, a number in the build) becomes a global label LBL "NAME"; a
               routine whose label is not reached by falling through starts its own Free42 program (END), so each
               program has its own local labels 00-99 for the structures. XEQ / GTO n -> XEQ / GTO "NAME".
  STRUCT       IF / ELSE / ENDIF, DO / WHILE / ENDDO (the C47's structured programming; the HP-42S has none) ->
               the opposite test and GTO to local labels: <test> IF -> <not test> GTO a ... ELSE -> GTO b, LBL a ...
               ENDIF -> LBL b; DO -> LBL t; <test> WHILE -> <not test> GTO e; ENDDO -> GTO t, LBL e. A test with no
               opposite (FS?, BIT?) -> <test> GTO y, GTO a, LBL y. Free42 keeps each GTO's target after the first
               search, so the jumps cost nothing.
  stack        4 levels (Free42's big stack is a setting the user may not have on; the C47 simulator also models 4
               levels, and the program runs there); DROP as on the C47 (T copied down).
  matrices     INDEX, STOEL, RCLEL, NEWMAT as on the C47; STO J (the column; every one-row STO J has 1 in Y) -> STOIJ;
               STO J X<>Y STO I X<>Y -> STOIJ; STOSEQ -> STOEL J+; RCLSEQ -> RCLEL J+. Free42 reads an element
               directly (the C47 copies the whole matrix for each element command), so the engine is not slowed by
               the matrix size.
  bits         BSIGNED off (flag 78 clear: unsigned) and WSIZE n -> XEQ "zWSn" (FUNC 11); AND OR XOR NOT as on the C47 (the
               decimal Free42 of the DM42 keeps 64-bit words exact); SINT, →REAL, UNSIGN, 2COMPL, 1COMPL, SIGNMT
               (C47 integer types and modes) are not needed; BS? IND r -> XEQ "zBS"+r (FUNC 11, BIT?: a test; X as it was).
  strings      "..." -> XSTR "..." (a string in X, as on the C47); x→α r, αIP r -> XEQ "zXA"+r, "zAI"+r (ALPHA,
               XTOA / ARCL / AIP, XASTO r).
  registers    R00-R99 as on the C47 (SIZE 100); the C47's local registers R.nn -> variables "R.nn"; LocR, STOS,
               RCLS (the user's stack kept by the C47 program) are left out.
  other        CHS -> +/-; RAN# -> RAN; LASTx -> LASTX; DELITM -> CLV; MEM# -> 1E9 (no memory test: Free42 grows);
               STO L -> STO ST L; RCL Z -> RCL ST Z.
  screen/keys  the helpers of the program "z47" (see helpers()).

  python3 tools/build_free42.py        -> build/free42/CHESS47.txt (the Free42 listing; Paste it into Free42 or
                                           convert it to .raw)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'build', 'f42', 'CHESS47.txt')          # the f42 variant (tools/build_chess47.py)
LABELS = os.path.join(ROOT, 'build', 'f42', 'CHESS47_labels.txt')
OUT = os.path.join(ROOT, 'build', 'free42')

TESTS = {'X=Y?': 'X≠Y?', 'X≠Y?': 'X=Y?', 'X<Y?': 'X≥Y?', 'X≥Y?': 'X<Y?', 'X>Y?': 'X≤Y?', 'X≤Y?': 'X>Y?',
         'X=0?': 'X≠0?', 'X≠0?': 'X=0?', 'X<0?': 'X≥0?', 'X≥0?': 'X<0?', 'X>0?': 'X≤0?', 'X≤0?': 'X>0?'}
STRUCT = ('IF', 'ELSE', 'ENDIF', 'DO', 'WHILE', 'ENDDO')
LOCAL = ['%02d' % i for i in range(100)] + list('ABCDEFGHIJabcde')
DROPPED = {'SINT', '→REAL', 'UNSIGN', '2COMPL', '1COMPL', 'SIGNMT', 'LocR', 'REM'}
SIMPLE = {'CHS': ['+/-'], 'RAN#': ['RAN'], 'LASTx': ['LASTX'], 'MEM#': ['1E9'], 'STO L': ['STO ST L'],
          'RCL Z': ['RCL ST Z'], 'RCL Y': ['RCL ST Y'], 'RCL X': ['RCL ST X'], 'STRI?': ['STR?'], '1111#2': ['15'],
          'STOSEQ': ['STOEL', 'J+'], 'RCLSEQ': ['RCLEL', 'J+'], 'STOIJ': ['STOIJ']}


def label_names():
    names = {}
    for l in open(LABELS, encoding='utf-8'):
        m = re.match(r':(\w+):\s+(\d+)', l)
        if m:
            names[m.group(2)] = m.group(1)
    return names


def is_test(op):
    return op.endswith('?') or op.startswith(('BS? ', 'BC? ', 'FS? ', 'FC? ', 'ISG ', 'DSE ', 'XEQ "zBS', 'XEQ "zKQ'))


def command(s, names, used):
    """One C47 step -> Free42 steps (a list)."""
    op, _, arg = s.partition(' ')
    if s.startswith('"'):
        return ['XSTR ' + s]
    if op in DROPPED or s in DROPPED:
        return []
    if s in SIMPLE:
        return SIMPLE[s]
    if op in ('XEQ', 'GTO') and re.fullmatch(r'\d+', arg):
        return ['%s "%s"' % (op, names[arg])]
    if op == 'LBL' and re.fullmatch(r'\d+', arg):
        return ['LBL "%s"' % names[arg]]
    if op == 'WSIZE':
        used.add(('zWS', arg))
        return ['XEQ "zWS%s"' % arg]          # FUNC 11: the stack as it was
    m = re.fullmatch(r'STO([+-]) "(\w+)"', s)
    if m:                                     # the C47 creates a missing variable (as 0 + x); Free42: Nonexistent
        h = 'zP' if m.group(1) == '+' else 'zM'; used.add((h, m.group(2)))
        return ['XEQ "%s%s"' % (h, m.group(2))]
    if op == 'DELITM':
        return ['CLV ' + arg]
    if op == 'STOS':
        return []
    if op == 'RCLS':                          # the program's end: the normal screen (GrMod 0) again
        return ['0', 'STO "GrMod"', 'DROP']
    m = re.fullmatch(r'(STO|RCL|STO\+|STO-|STO×|STO÷|RCL\+|RCL-|RCL×|RCL÷) R\.(\d\d)', s)
    if m:
        return ['%s "R.%s"' % (m.group(1), m.group(2))]
    if op == 'BS?' and arg.startswith('IND '):
        r = arg[4:]; used.add(('zBS', r))
        return ['XEQ "zBS%s"' % r]
    if op in ('x→α', 'αIP'):
        h = 'zXA' if op == 'x→α' else 'zAI'; used.add((h, arg))
        return ['XEQ "%s%s"' % (h, arg)]
    if op == 'KEY?':
        used.add(('zKQ', arg))
        return ['XEQ "zKQ%s"' % arg]
    if op == 'PAUSE':
        return [arg, 'XEQ "zW"']
    if op == 'TICKS':
        return ['XEQ "zTK"']
    if op == 'ATEXT':
        return ['XEQ "zAT"']                  # the string in Z, X column, Y row (C47); X, Y the next position
    if op == 'GRFNT':
        return ['STO "zFN"']
    if op == 'GRMOD':
        return ['XEQ "zGM"']                  # the mode in X (kept): flags 34 / 35
    if op == 'AGRAPH':
        return ['XEQ "zAG%s"' % arg]          # one column of WSIZE pixels from the register
    if s == 'R-CLR':
        return ['XEQ "zRC"']                  # X = sss.nn: nn registers from Rsss cleared (X stays)
    if op == 'CLLCD':
        return ['CLLCD']
    return [s]


def convert(lines, names):
    """The C47 listing -> Free42 programs (lists of steps)."""
    used = set()
    progs, cur = [], []
    prev = None
    # pass 1: steps, routine starts, the structure steps kept as markers
    seq = []
    lines = [l.strip() for l in lines]
    i = 0
    while i < len(lines):
        s = lines[i]; i += 1
        if s == 'STO J' and lines[i:i + 3] == ['X<>Y', 'STO I', 'X<>Y']:
            seq.append(('C', 'STOIJ')); i += 3; continue          # (I, J) from Y, X: the stack as it was
        if s == 'STO J':                                            # a one-row matrix: J from X, I = 1 (in Y:
            seq.append(('C', 'STOIJ')); continue                     # every one-row STO J of the source has 1 there)
        assert s not in ('STO I', 'RCL I', 'RCL J'), s
        if not s or s == 'END':
            continue
        op, _, arg = s.partition(' ')
        if op in STRUCT:
            seq.append(('S', op, arg))
            continue
        if op == 'LBL' and re.fullmatch(r'\d+', arg):
            seq.append(('L', names[arg], prev in ('RTN', 'GTO')))
        elif op == 'LBL':
            seq.append(('L', arg.strip('"'), True))
        else:
            for c in command(s, names, used):
                seq.append(('C', c))
        prev = op if op in ('RTN', 'GTO') else s
    # pass 2: programs, structures
    progs, cur, lab, stack, pending = [], [], [], [], []
    def newlab():
        if not lab:
            raise SystemExit('more than 115 local labels in program %s' % cur[0])
        return lab.pop(0)
    for item in seq:
        if item[0] == 'L':
            name, newprog = item[1], item[2]
            if newprog or not cur:
                if cur:
                    assert not stack, 'structure open across %s' % name
                    progs.append(cur + ['END'])
                cur, lab = [], list(LOCAL)
            cur.append('LBL "%s"' % name)
            continue
        if item[0] == 'C':
            cur.append(item[1]); continue
        _, op, num = item
        if op in ('IF', 'WHILE'):
            t = cur.pop()
            assert is_test(t), 'no test before %s %s: %s' % (op, num, t)
            if op == 'IF':
                a = newlab(); stack.append(['IF', num, a, None])
            else:
                fr = [f for f in stack if f[0] == 'DO' and f[1] == num][-1]
                a = fr[3]
            if t in TESTS:
                cur += [TESTS[t], 'GTO ' + a]
            else:
                y = newlab()
                cur += [t, 'GTO ' + y, 'GTO ' + a, 'LBL ' + y]
        elif op == 'ELSE':
            fr = stack[-1]; assert fr[0] == 'IF' and fr[1] == num
            b = newlab(); cur += ['GTO ' + b, 'LBL ' + fr[2]]; fr[2] = b
        elif op == 'ENDIF':
            fr = stack.pop(); assert fr[0] == 'IF' and fr[1] == num
            cur.append('LBL ' + fr[2])
        elif op == 'DO':
            t, e = newlab(), newlab(); stack.append(['DO', num, t, e]); cur.append('LBL ' + t)
        elif op == 'ENDDO':
            fr = stack.pop(); assert fr[0] == 'DO' and fr[1] == num
            cur += ['GTO ' + fr[2], 'LBL ' + fr[3]]
    progs.append(cur + ['END'])
    return progs, used


def helpers(used):
    """The program z47: Free42 versions of the C47's screen, key and string commands."""
    L = ['LBL "z47"', 'RTN']
    for h, r in sorted(used):
        if h == 'zBS':      # BS? IND r: bit (r) of X set? a test (FUNC 00: the stack as it was)
            L += ['LBL "zBS%s"' % r, 'FUNC 11', 'RCL %s' % r, 'BIT?', 'GTO 01', 'DROP', 'RTNNO', 'LBL 01', 'DROP',
                  'RTNYES']
        elif h == 'zXA':    # x→α r: X (a string, or a character code) appended to the string in r
            L += ['LBL "zXA%s"' % r, 'FUNC 11', 'CLA', 'ARCL %s' % r, 'STR?', 'GTO 01', 'XTOA', 'GTO 02',
                  'LBL 01', 'ARCL ST X', 'LBL 02', 'XASTO %s' % r, 'RTN']
        elif h == 'zAI':    # αIP r: the integer part of X appended (r a number: its digits first)
            L += ['LBL "zAI%s"' % r, 'FUNC 11', 'CLA', 'RCL %s' % r, 'STR?', 'GTO 01', 'AIP', 'GTO 02',
                  'LBL 01', 'ARCL ST X', 'LBL 02', 'DROP', 'AIP', 'XASTO %s' % r, 'RTN']
        elif h == 'zWS':    # WSIZE n (the C47's argument): the stack as it was
            L += ['LBL "zWS%s"' % r, 'FUNC 11', '%s' % r, 'WSIZE', 'DROP', 'RTN']
        elif h in ('zP', 'zM'):    # STO+ / STO- "name", the name created when missing (flag 25: the error ignored)
            L += ['LBL "%s%s"' % (h, r), 'FUNC 11', 'SF 25', 'RCL "%s"' % r, 'FS?C 25', 'GTO 01']
            L += (['STO "%s"' % r] if h == 'zP' else ['+/-', 'STO "%s"' % r, '+/-']) + ['RTN']
            L += ['LBL 01', 'X<>Y', 'STO%s "%s"' % ('+' if h == 'zP' else '-', r), 'RTN']
        elif h == 'zKQ':    # KEY? r: a key (C47 code) in r and the next step skipped... as the C47: the test
            # a key read by a pause (zW) first (zPK)
            L += ['LBL "zKQ%s"' % r, 'FUNC 00', 'RCL "zPK"', 'X≠0?', 'GTO 01', 'GETKEYA', 'X=0?', 'RTNYES',
                  'LBL 01', '0', 'STO "zPK"', 'DROP', 'XEQ "zKM"', 'STO %s' % r, 'RTNNO']
    # R-CLR: X = sss.nn -> 0 into Rsss ... Rsss+nn-1 (an ISG counter sss.eee); FUNC 11 (X given back): the stack as it was
    L += ['LBL "zRC"', 'FUNC 11', 'STO "zV"', 'IP', 'STO "zI"', 'LASTX', 'FP', '100', '×', 'IP', 'RCL+ "zI"', '1', '-',
          '1000', '÷', 'STO+ "zI"', 'LBL 01', '0', 'STO IND "zI"', 'ISG "zI"', 'GTO 01', 'RCL "zV"', 'RTN']
    L += screen()
    # one program for each helper (each with its own local labels 01, 02: GTO searches the whole program)
    progs, cur = [], []
    for st in L:
        if st.startswith('LBL "') and cur:
            progs.append(cur + ['END']); cur = []
        cur.append(st)
    return progs + [cur + ['END']]


# ------------------------------------------------------------------------------------------------ the screen
# The DM42's Free42: 3 STO "GrMod" gives AGRAPH the whole 400 x 240 screen, origin (1, 1) at the top left; AGRAPH draws
# ALPHA, one character = one column of 8 pixels, bit 0 at the top, at row Y, column X. Flags 34 / 35 (the HP-42S's
# AGRAPH control): CF CF = OR, CF SF = set, SF CF = clear, SF SF = XOR (GRMOD 0 1 2 3 on the C47). The C47 counts rows
# from the bottom (row r of the C47 = row 240 - r here) and columns from 0. The fonts and the glyphs go to registers as
# strings of column bytes (built here, kept by zDAT): no INDEX (Free42 has one indexed matrix, the program's).
REG_STD, REG_TINY, REG_GL, SIZE = 100, 800, 1100, 1300
GMODE = {0: ('CF 34', 'CF 35'), 1: ('CF 34', 'SF 35'), 2: ('SF 34', 'CF 35'), 3: ('SF 34', 'SF 35')}
HPCHR = {0: '÷', 1: '×'}
HPCHR.update({c: chr(c) for c in range(32, 127) if c != 94})


def esc(b):
    """Bytes -> a Free42 string literal (€ and two hex digits: any character code, as Free42's Paste reads it)."""
    return ''.join(chr(x) if 48 <= x <= 57 or 65 <= x <= 90 or 97 <= x <= 122 else '€%02X' % x for x in b)


def font_columns(glyph, cp=0):
    """A glyph of stdfont / tinyfont -> (bands of column bytes, advance)."""
    cb, cg, ca, ra, rg, rb, rows = glyph
    lh, w = ra + rg + rb, cb + cg + ca
    on = lambda x, y: cb <= x < cb + cg and 0 <= y - ra < len(rows) and rows[y - ra] >> (cg - 1 - (x - cb)) & 1
    bands = []
    for b in range((lh + 7) // 8):
        bands.append([sum(1 << k for k in range(8) if 8 * b + k < lh and on(x, 8 * b + k)) for x in range(w)])
    return bands, w


def glyph_rows():
    """GL (the C47 program's glyph matrix, 32 x 24 words: bit i at row y + i from the bottom) from the C47 simulator."""
    sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tests')]
    import chess47sim as S
    shots, c = S.run([])
    return [[int(w) for w in row] for row in c.mats['GL']]


def data():
    """The program zDAT: the fonts (R100 + 5 code + band 0-2, the advance at + 3, the mask of band 2 at + 4; the tiny
    font R800 + 2 code, + 1 its advance) and the glyphs (R1100 + 6 row + band, + 3 + band inverted)."""
    sys.path.insert(0, os.path.join(ROOT, 'python'))
    from stdfont import STD, code as stdcode
    from tinyfont import TINY
    L = ['LBL "zDAT"']
    for hp, ch in sorted(HPCHR.items()):
        g = STD.get(stdcode(ch), STD[0x3f])
        bands, w = font_columns(g)
        r = REG_STD + 5 * hp
        for b, cols in enumerate(bands):
            L += ['XSTR "%s"' % esc(cols), 'STO %d' % (r + b)]
        L += [str(w), 'STO %d' % (r + 3), 'XSTR "%s"' % esc([15] * w), 'STO %d' % (r + 4)]
        g = TINY.get(stdcode(ch), TINY[0x3f])
        bands, w = font_columns(g)
        assert len(bands) == 1
        L += ['XSTR "%s"' % esc(bands[0]), 'STO %d' % (REG_TINY + 2 * hp), str(w), 'STO %d' % (REG_TINY + 2 * hp + 1)]
    frame = [16777215 if abs(24 - k - 12.5) > 10 else 12582915 for k in range(24)]     # R33 24 ... 1, left to right
    for g, row in enumerate(glyph_rows() + [frame]):
        r = REG_GL + 6 * g
        for inv in (0, 1):
            ws = [(~w if inv else w) & 0xFFFFFF for w in row]
            for b in range(3):
                cols = [sum(1 << k for k in range(8) if ws[x] >> (23 - 8 * b - k) & 1) for x in range(24)]
                L += ['XSTR "%s"' % esc(cols), 'STO %d' % (r + 3 * inv + b)]
    # STO nnn above 99: through IND (the address pushed first: STO IND ST Y, then both dropped)
    out = []
    for i, st in enumerate(L):
        m = re.fullmatch(r'STO (\d+)', st)
        if m:
            out[-1:] = [m.group(1), out[-1], 'STO IND ST Y', 'DROP', 'DROP']
        else:
            out.append(st)
    return out + ['RTN']


def screen():
    L = []
    # GRMOD (X kept): the mode for zAT, zAG99, zSQ; GRFNT: STO "zFN"
    L += ['LBL "zGM"', 'STO "zGV"', 'RTN']
    # zAT: ATEXT Z (the C47): the string in Z, X its column, Y the row of the bottom of the glyph box; X, Y become the
    # next position (|X|, |Y| used; a negative one grows in magnitude). Fonts: zFN 10 the tiny one (8 rows), 20 the
    # standard one (20 rows: bands of 8, 8, 4), 21 the same one column narrower. A line break before a character that
    # would pass column 400 (once past 380), and after the text past 380; LF / CR (10, 13) a new line.
    L += ['LBL "zAT"', 'FUNC 33', 'STO "zX0"', 'X<>Y', 'STO "zY0"', 'X<>Y', 'RCL ST Z', 'STO "zS0"', 'STO "zS"',
          'DROP', 'RCL "zX0"', 'ABS', 'STO "zx"', 'STO "zx0"', 'RCL "zY0"', 'ABS', 'STO "zln"', 'STO "zy"',
          '20', 'STO "zLH"', '0', 'STO "zCP"', 'STO "zT"', 'RCL "zFN"', '21', 'X=Y?', 'GTO 01', '10', 'RCL "zFN"', 'X≠Y?',
          'GTO 02', '8', 'STO "zLH"', '1', 'STO "zT"', 'GTO 02', 'LBL 01', '1', 'STO "zCP"',
          # each character
          'LBL 02', 'CLA', 'ARCL "zS"', 'ALENG', 'X=0?', 'GTO 90', 'ATOX', 'STO "zc"', 'XASTO "zS"',
          '10', 'X=Y?', 'GTO 20', '13', 'X=Y?', 'GTO 20', 'RCL "zc"', '127', 'X≥Y?', 'GTO 03', '63', 'STO "zc"',
          'LBL 03', 'RCL "zT"', 'X≠0?', 'GTO 04',
          'RCL "zc"', '5', '×', '%d' % REG_STD, '+', 'STO "zr"', '3', '+', 'RCL IND ST X', 'GTO 05',
          'LBL 04', 'RCL "zc"', '2', '×', '%d' % REG_TINY, '+', 'STO "zr"', '1', '+', 'RCL IND ST X',
          'LBL 05', 'RCL- "zCP"', 'STO "zad"',
          # past column 380 and the character would pass 400: a new line
          'RCL "zx"', '380', 'X≥Y?', 'GTO 06', 'RCL "zx"', 'RCL+ "zad"', '400', 'X≥Y?', 'GTO 06',
          'RCL "zx0"', 'STO "zx"', 'RCL "zLH"', 'STO- "zln"',
          'LBL 06', '240', 'RCL "zln"', '-', 'RCL- "zLH"', '1', '+', 'STO "ztp"', 'RCL "zx"', '1', '+', 'STO "zcl"',
          # the bands: zGV 1 (the box cleared first): bands 0, 1 set, band 2 its 4 rows cleared (mask) then OR'd
          'RCL "zGV"', '1', 'X≠Y?', 'GTO 07', 'CF 34', 'SF 35', 'RCL "zT"', 'X≠0?', 'GTO 08',
          '0', 'XEQ 40', '1', 'XEQ 40', 'SF 34', 'CF 35', 'CLA', 'RCL "zr"', '4', '+', 'RCL IND ST X', 'ARCL ST X',
          'RCL "ztp"', '16', '+', 'RCL "zcl"', 'AGRAPH', 'CF 34', 'CF 35', '2', 'XEQ 40', 'GTO 09',
          'LBL 08', '0', 'XEQ 40', 'GTO 09',
          'LBL 07', 'XEQ 45', '0', 'XEQ 40', 'RCL "zT"', 'X≠0?', 'GTO 09', '1', 'XEQ 40', '2', 'XEQ 40',
          'LBL 09', 'RCL "zad"', 'STO+ "zx"', 'GTO 02',
          'LBL 20', 'RCL "zx0"', 'STO "zx"', 'RCL "zLH"', 'STO- "zln"', 'GTO 02',
          # the end: past 380 a new line; X, Y the next position
          'LBL 90', 'RCL "zx"', '380', 'X≥Y?', 'GTO 91', 'RCL "zx0"', 'STO "zx"', 'RCL "zLH"', 'STO- "zln"',
          'LBL 91', 'RCL "zS0"', 'RCL "zln"', 'RCL- "zy"', 'RCL "zY0"', 'X<0?', 'GTO 92', 'X<>Y', 'GTO 93',
          'LBL 92', 'X<>Y', '+/-', 'LBL 93', '+', 'RCL "zx"', 'RCL- "zx0"', 'RCL "zX0"', 'X<0?', 'GTO 94',
          'X<>Y', 'GTO 95', 'LBL 94', 'X<>Y', '+/-', 'LBL 95', '+', 'RTN',
          # band X of the character zr at (ztp + 8 X, zcl) in the flags' mode
          'LBL 40', 'CLA', 'ENTER', 'RCL+ "zr"', 'RCL IND ST X', 'ARCL ST X', 'DROP', 'DROP', '8', '×',
          'RCL+ "ztp"', 'RCL "zcl"', 'AGRAPH', 'DROP', 'DROP', 'RTN',
          # the flags for zGV 0, 2, 3
          'LBL 45', 'RCL "zGV"', '2', 'X=Y?', 'GTO 46', '3', 'X=Y?', 'GTO 47', 'CF 34', 'CF 35', 'RTN',
          'LBL 46', 'SF 34', 'CF 35', 'RTN', 'LBL 47', 'SF 34', 'SF 35', 'RTN']
    # zAG99: AGRAPH 99 (the C47): the 24-bit word R99 as one column, bit i at row Y + i from the bottom, column X;
    # X + 1 after. zGV 0 OR, 1 set, 2 clear, 3 XOR, 4 the inverse set. Bit by bit (BIT?): slow, a few columns only.
    L += ['LBL "zAG99"', 'FUNC 22', 'STO "zgx"', 'X<>Y', 'STO "zgy"', 'X<>Y', 'RCL "zGV"', 'XEQ 60',
          '0', 'STO "zgb"',
          'LBL 01', '0', 'STO "zgv"', '0', 'STO "zgk"',
          'LBL 02', 'RCL 99', '23', 'RCL "zgb"', '8', '×', '-', 'RCL- "zgk"', 'BIT?', 'GTO 03', 'GTO 04',
          'LBL 03', '2', 'RCL "zgk"', 'Y↑X', 'STO+ "zgv"', 'LBL 04', 'DROP', 'DROP', '1', 'STO+ "zgk"', '8',
          'RCL "zgk"', 'X<Y?', 'GTO 02', 'RCL "zGV"', '4', 'X≠Y?', 'GTO 05', '255', 'RCL- "zgv"', 'STO "zgv"',
          'LBL 05', 'CLA', 'RCL "zgv"', 'XTOA', 'DROP', '240', 'RCL "zgy"', '-', '23', '-', 'RCL "zgb"', '8', '×', '+',
          'RCL "zgx"', '1', '+', 'AGRAPH', 'DROP', 'DROP', '1', 'STO+ "zgb"', '3', 'RCL "zgb"', 'X<Y?', 'GTO 01',
          'RCL "zgy"', 'RCL "zgx"', '1', '+', 'RTN',
          'LBL 60', '4', 'X=Y?', 'GTO 61', 'X<>Y', '1', 'X=Y?', 'GTO 61', '2', 'X=Y?', 'GTO 62', '3', 'X=Y?', 'GTO 63',
          'CF 34', 'CF 35', 'RTN', 'LBL 61', 'CF 34', 'SF 35', 'RTN', 'LBL 62', 'SF 34', 'CF 35', 'RTN',
          'LBL 63', 'SF 34', 'SF 35', 'RTN']
    # zSQ: the square of DRAWSQ: the glyph row R36 at column R30, bottom row R31 (C47), framed (the cursor) when R32,
    # inverted (picked) when R35: (glyph OR frame), inverted when picked = the inverse glyph, frame cleared. R30 + 24
    # and R33 0 after, as the C47's 24 AGRAPH columns leave them.
    L += ['LBL "zSQ"', '240', 'RCL- 31', '23', '-', 'STO "zqy"', 'RCL 30', '1', '+', 'STO "zqx"',
          'RCL 36', '1', '-', '6', '×', '%d' % REG_GL, '+', 'RCL 35', 'X≠0?', '3', 'X=0?', 'CLX', '+', 'STO "zqr"',
          'CF 34', 'SF 35', '0', 'XEQ 10', '1', 'XEQ 10', '2', 'XEQ 10',
          'RCL 32', 'X=0?', 'GTO 02', 'CF 34', 'CF 35', 'RCL 35', 'X≠0?', 'SF 34',
          '%d' % (REG_GL + 6 * 32), 'STO "zqr"', '0', 'XEQ 10', '1', 'XEQ 10', '2', 'XEQ 10',
          'LBL 02', '24', 'STO+ 30', '0', 'STO 33', 'RTN',
          'LBL 10', 'CLA', 'ENTER', 'RCL+ "zqr"', 'RCL IND ST X', 'ARCL ST X', 'DROP', 'DROP', '8', '×',
          'RCL+ "zqy"', 'RCL "zqx"', 'AGRAPH', 'DROP', 'DROP', 'RTN']
    # zW: PAUSE n (tenths of a second, n in X: FUNC 10); a key ends it (kept in zPK for KEY?); flag 09 (the tests): no wait
    L += ['LBL "zW"', 'FUNC 10', 'FS? 09', 'RTN', 'XEQ "zTK"', '+', 'STO "zwe"',
          'LBL 01', 'GETKEYA', 'X≠0?', 'GTO 02', 'DROP', 'XEQ "zTK"', 'RCL "zwe"', 'X>Y?', 'GTO 01', 'RTN',
          'LBL 02', 'STO "zPK"', 'RTN']
    # zTK: TICKS (tenths of a second of the day); zKM: GETKEY code -> the C47 key code (rows 2-8 of the C47's
    # numbering: 21-26, 31-36, 41-45, 51-55 ... 81-85)
    L += ['LBL "zTK"', 'TIME', '→HR', '36000', '×', 'IP', 'RTN']
    L += ['LBL "zKM"', 'FUNC 11', '6', 'X<Y?', 'GTO 01', '+', '20', '+', 'RTN',
          'LBL 01', 'DROP', '12', 'X<Y?', 'GTO 02', '+', '24', '+', 'RTN',
          'LBL 02', 'DROP', '13', '-', 'RCL ST X', '5', 'MOD', '1', '+', 'X<>Y', '5', '÷', 'IP', '4', '+', '10', '×', '+', 'RTN']
    return L


def main():
    names = label_names()
    lines = open(SRC, encoding='utf-8').read().split('\n')
    progs, used = convert(lines, names)
    # the start: big stack, unsigned words, 100 registers
    first = progs[0]
    assert first[0] == 'LBL "CHESS47"'
    first[1:1] = ['FS? 78', 'BSIGNED', 'SIZE %04d' % SIZE, '3', 'STO "GrMod"', 'DROP', '20', 'STO "zFN"', 'DROP',
                  '0', 'STO "zGV"', 'STO "zPK"', 'DROP', 'XEQ "zDAT"']
    os.makedirs(OUT, exist_ok=True)
    allp = progs + helpers(used) + [data() + ['END']]
    with open(os.path.join(OUT, 'CHESS47.txt'), 'w', encoding='utf-8') as f:
        for p in allp:
            f.write('\n'.join(p) + '\n')
    n = sum(len(p) for p in allp)
    print('build/free42/CHESS47.txt: %d programs, %d steps' % (len(allp), n))


if __name__ == '__main__':
    main()
