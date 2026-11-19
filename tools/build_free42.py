#!/usr/bin/env python3
"""build_free42.py - CHESS47 for Free42 on the SwissMicros DM42 / DM42n (stock firmware, Free42 3.3), converted
from the C47 program (build/draw/CHESS47.txt, the drawn pieces), step for step where Free42 can do the same:

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
SRC = os.path.join(ROOT, 'build', 'draw', 'CHESS47.txt')
LABELS = os.path.join(ROOT, 'listings', 'CHESS47_labels.txt')
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
    if op in ('STOS', 'RCLS'):
        return []
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
            L += ['LBL "zKQ%s"' % r, 'FUNC 00', 'GETKEYA', 'X=0?', 'RTNNO', 'XEQ "zKM"', 'STO %s' % r, 'RTNYES']
    # R-CLR: X = sss.nn -> 0 into Rsss ... Rsss+nn-1 (an ISG counter sss.eee); FUNC 11 (X given back): the stack as it was
    L += ['LBL "zRC"', 'FUNC 11', 'STO "zV"', 'IP', 'STO "zI"', 'LASTX', 'FP', '100', '×', 'IP', 'RCL+ "zI"', '1', '-',
          '1000', '÷', 'STO+ "zI"', 'LBL 01', '0', 'STO IND "zI"', 'ISG "zI"', 'GTO 01', 'RCL "zV"', 'RTN']
    # stubs of the screen for now
    L += ['LBL "zAT"', 'RTN', 'LBL "zGM"', 'RTN', 'LBL "zAG99"', 'RTN',
          'LBL "zW"', 'DROP', 'RTN', 'LBL "zTK"', 'TIME', '→HR', '36000', '×', 'IP', 'RTN',
          'LBL "zKM"', 'RTN']
    # one program for each helper (each with its own local labels 01, 02: GTO searches the whole program)
    progs, cur = [], []
    for st in L:
        if st.startswith('LBL "') and cur:
            progs.append(cur + ['END']); cur = []
        cur.append(st)
    return progs + [cur + ['END']]


def main():
    names = label_names()
    lines = open(SRC, encoding='utf-8').read().split('\n')
    progs, used = convert(lines, names)
    # the start: big stack, unsigned words, 100 registers
    first = progs[0]
    assert first[0] == 'LBL "CHESS47"'
    first[1:1] = ['FS? 78', 'BSIGNED', 'SIZE 0100']
    os.makedirs(OUT, exist_ok=True)
    allp = progs + helpers(used)
    with open(os.path.join(OUT, 'CHESS47.txt'), 'w', encoding='utf-8') as f:
        for p in allp:
            f.write('\n'.join(p) + '\n')
    n = sum(len(p) for p in allp)
    print('build/free42/CHESS47.txt: %d programs, %d steps' % (len(allp), n))


if __name__ == '__main__':
    main()
