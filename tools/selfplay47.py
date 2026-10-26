#!/usr/bin/env python3
"""selfplay47.py - the rules check: CHESS47 (build/CHESS47.txt, in the C47 simulator) plays itself (key 9, C47 vs
C47) GAMES games at each level, and python-chess (pip install chess) checks the whole game:

  - every move is legal (promotion: always a queen), and after every move the C47's board is python-chess's;
  - the game ends exactly when the rules say: CHECKMATE and STALEMATE as python-chess, DRAW: REPETITION at the third
    time of a position (the same side to move), DRAW: MATERIAL when no side can mate (python-chess's
    is_insufficient_material; the C47 counts kings with at most one bishop or knight, so two bishops on one colour
    are reported as a note, not an error);
  - the clock: only a person's runs (5 minutes + 10 s a move), so C47 vs C47 never ends on time (an error if it
    does); the time-out rule itself (FIDE 6.9) is in tests/test_chess47.py;
  - the status line says the same as python-chess.

The simulator's time is its step count (0.17 ms a step, Almanac 47's measure on the C47), so the clock runs as it
would on the calculator. A game still going after MAXPLY plies (the record holds 299) stops unfinished (no error).
Level 0 (CRAZY, random moves) plays long games fast; level 2 is the slowest (the C47 thinks 10-25 s a move: a
game of 100 plies is about 10 M steps here). Each game has its own seed (the book's choice, CRAZY).

  python3 tools/selfplay47.py                     5 games at levels 0, 1 and 2  -> docs/SELFPLAY.md
  python3 tools/selfplay47.py 2 1                 2 games at level 1
  python3 tools/selfplay47.py 5 0,1,2 100         5 games a level, the first seed 100
The exit code is 1 when a game broke a rule (the error and the game are in the report)."""
import os, sys, time
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import chess                                                     # noqa: E402
import c47sim                                                    # noqa: E402
import chess47sim as S                                           # noqa: E402

MAXPLY = 290
STATUS_X, STATUS_ROW = 212, 156                                  # LBL :STATUS:'s text (ATEXT at x 212, row 156)


def sq(s):
    """A square of the mailbox -> python-chess."""
    return chess.square((s - 1) % 10 - 1, (s - 1) // 10 - 2)


def mb(q):
    return 10 * (chess.square_rank(q) + 2) + chess.square_file(q) + 2


def c47_material_draw(b):
    """The C47's DRAW: MATERIAL: no pawn, rook or queen and at most one bishop or knight on the board."""
    if b.pawns | b.rooks | b.queens:
        return False
    return chess.popcount(b.knights | b.bishops) <= 1


def expected_end(b):
    """What the rules say after the last move (no time-out): a text of the C47's status line, or None."""
    if b.is_checkmate():
        return 'CHECKMATE'
    if b.is_stalemate():
        return 'STALEMATE'
    if b.is_repetition(3):
        return 'DRAW: REPETITION'
    if c47_material_draw(b):
        return 'DRAW: MATERIAL'
    return None


def board_repetition(b):
    """The position of the pieces with the same side to move the third time (castling and en passant rights left
    out, as the C47's key)."""
    t, n = b.copy(), 0
    key = (t.board_fen(), t.turn)
    while True:
        if (t.board_fen(), t.turn) == key:
            n += 1
        if not t.move_stack:
            break
        t.pop()
    return n >= 3


def game(level, seed):
    b = chess.Board()
    c = c47sim.load([S.PROG])
    c.s = [D(0)] * 4; c.pix = []; c.keys = []; c.steps = 0; c.frames = []
    c.seed = seed
    presses = {2: [], 1: [S.LEVEL], 0: [S.LEVEL, S.LEVEL]}[level]
    st = {'synced': 0, 'err': None, 'note': None, 'status': '', 'started': False, 'end': None, 'keys': presses + [S.AUTO]}

    def sync():
        """The moves of the game record GH not yet on b: each one legal, then pushed."""
        row = c.mats['GH'][0]
        while st['synced'] < len(row) and int(row[st['synced']]):
            m = int(row[st['synced']])
            f, t = sq(m // 1000), sq(m % 1000)
            mv = chess.Move(f, t)
            if b.piece_at(f) and b.piece_at(f).piece_type == chess.PAWN and chess.square_rank(t) in (0, 7):
                mv = chess.Move(f, t, chess.QUEEN)
            if mv not in b.legal_moves:
                st['err'] = 'ply %d: illegal move %s in %s' % (b.ply() + 1, mv.uci(), b.fen()); raise StopIteration
            b.push(mv)
            st['synced'] += 1
            if b.ply() < MAXPLY and not int(c.reg.get('97', 0)):
                want = expected_end(b)
                if want is not None and st['synced'] == sum(1 for v in row if int(v)):
                    st['end'] = want                              # the C47 must stop here

    def check_board():
        bd = S.board(c)
        for q in chess.SQUARES:
            p = b.piece_at(q)
            want = 0 if p is None else (p.piece_type if p.color else -p.piece_type)
            if bd[mb(q)] != want:
                st['err'] = 'ply %d: the board differs at %s: C47 %s, python-chess %s (%s)' % (
                    b.ply(), chess.square_name(q), bd[mb(q)], want, b.fen())
                raise StopIteration

    def finish():
        """The game is over on the C47 (R97 = 1): the reason must be the rules'."""
        sync(); check_board()
        tw, tb = c.reg.get('TW'), c.reg.get('TB')
        st['tw'], st['tb'] = tw, tb
        text = st['status']
        if 'TIME' in text:                                       # C47 vs C47: no clock runs (only a person's)
            st['err'] = 'the C47 lost on time (%s): only a person\'s clock should run' % text
            return text
        if False:
            loser = b.turn                                       # the side to move ran out
            if (tw if loser else tb) != 0:
                st['err'] = '%s: the clock of the side to move is %s, not 0' % (text, tw if loser else tb)
            elif expected_end(b) is not None:
                st['err'] = '%s, but the position was already over: %s' % (text, expected_end(b))
            else:
                want = ('DRAW: TIME, NO MATE' if b.has_insufficient_material(not loser) else
                        '%s LOST ON TIME' % ('WHITE' if loser else 'BLACK'))
                if text != want:
                    st['err'] = 'time-out: the C47 says %s, the rules %s (%s)' % (text, want, b.fen())
            return text
        want = expected_end(b)
        if want is None and text == 'DRAW: REPETITION' and board_repetition(b):
            st['note'] = ('the third repetition of the pieces and the side to move, with other castling or en passant '
                          'rights (the C47 leaves them out of its key: README)')
        elif want is None:
            st['err'] = 'the C47 ended the game (%s) where the rules go on: %s' % (text, b.fen())
        elif text != want:
            st['err'] = 'the C47 says %s, the rules %s (%s)' % (text, want, b.fen())
        return text

    def hook(op, x):
        if op == 'ATEXT' and len(c.s) > 2 and c.s[0] == STATUS_X and c.s[1] == STATUS_ROW and isinstance(c.s[2], str):
            if c.s[2].strip():
                st['status'] = c.s[2].strip()
            return
        if op != 'KEY?':
            return
        if st['keys']:                                           # the level, then 9
            c.keys = [st['keys'].pop(0)]; return
        if 'GH' not in c.mats:
            return
        sync(); check_board()
        if int(c.reg.get('97', 0)):
            st['result'] = finish(); c.keys = [S.END]; return
        if st['end'] is not None:
            st['err'] = 'the C47 did not stop: the rules say %s (%s)' % (st['end'], b.fen()); raise StopIteration
        if b.ply() >= MAXPLY:
            st['result'] = 'unfinished at %d plies' % b.ply()
            st['tw'], st['tb'] = c.reg.get('TW'), c.reg.get('TB'); c.keys = [S.END]; return
        c.keys = [None]                                          # no key: the C47 plays on
    c.count = hook
    t0 = time.time()
    try:
        c.run('CHESS47', maxsteps=10 ** 11)
    except StopIteration:
        pass
    if st['err'] is None and not st.get('result'):
        st['err'] = 'the run stopped before the end of the game'
    if b.is_insufficient_material() and not c47_material_draw(b) and not st['err']:
        st['note'] = 'no mating material (bishops on one colour): python-chess calls it a draw, the C47 plays on'
    res = st.get('result') or '-'
    return dict(level=level, seed=seed, result=res, plies=b.ply(), err=st['err'], note=st['note'],
                tw=st.get('tw'), tb=st.get('tb'), secs=time.time() - t0, steps=c.steps,
                san=chess.Board().variation_san(b.move_stack))


def mmss(t):
    if t is None:
        return '-'
    t = int(t)
    return '%d:%02d' % (t // 600, t // 10 % 60)


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    levels = [int(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0, 1, 2]
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rows, bad = [], 0
    for level in levels:
        for g in range(games):
            r = game(level, seed0 + 100 * level + g)
            rows.append(r)
            bad += bool(r['err'])
            print('level %d game %d (seed %d): %-24s %3d plies  W %s B %s  %s  (%.0f s here, %.1f M steps)' % (
                level, g + 1, r['seed'], r['result'], r['plies'], mmss(r['tw']), mmss(r['tb']),
                'ERROR: ' + r['err'] if r['err'] else 'rules kept' + (' (note: %s)' % r['note'] if r['note'] else ''),
                r['secs'], r['steps'] / 1e6), flush=True)
    md = ['# Chess 47 against itself: the rules check', '',
          '`python3 tools/selfplay47.py %s`: CHESS47 in the C47 simulator plays itself (key 9), python-chess checks '
          'every move, the board after it and the end of the game.' %
          ' '.join(sys.argv[1:]), '',
          '| level | seed | result | plies | clock W | clock B | check |', '|---|---|---|---|---|---|---|']
    for r in rows:
        md.append('| %d | %d | %s | %d | %s | %s | %s |' % (r['level'], r['seed'], r['result'], r['plies'], mmss(r['tw']),
                  mmss(r['tb']), 'ERROR: ' + r['err'] if r['err'] else 'rules kept' + ('; ' + r['note'] if r['note'] else '')))
    md += ['', '## The games', '']
    for r in rows:
        md += ['**Level %d, seed %d: %s**' % (r['level'], r['seed'], r['result']), '', r['san'] or '-', '']
    with open(os.path.join(ROOT, 'docs', 'SELFPLAY.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    print('%d games, %s -> docs/SELFPLAY.md' % (len(rows), 'all kept the rules' if not bad else '%d broke a rule' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
