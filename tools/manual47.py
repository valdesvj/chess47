"""manual47.py - the screens of docs/MANUAL.md, made in the C47 simulator (python/chess47sim.py) from the keys, as you
would press them on the calculator. python3 tools/manual47.py writes docs/manual/*.png and prints what each shows."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import chess47sim as S                                           # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'manual')
DIV, TWO = 55, 74                                                # ÷ (Chess960), 3 (two players)


def shot(name, keys, what):
    shots, c = S.run(keys)
    S.png(os.path.join(OUT, name + '.png'), shots[-1])
    hist = [x for x in (c.reg.get(str(r)) for r in range(73, 80)) if isinstance(x, str)]
    print('docs/manual/%s.png: %s (%s)' % (name, what, ' '.join(hist)))
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    U, D, L, R, P = S.UP, S.DOWN, S.LEFT, S.RIGHT, S.PICK
    shot('1_start', [], 'the start: white to move, the cursor on e2')
    shot('2_pick', [P], 'e2 picked: the piece shown inverted')
    shot('3_reply', [P, U, U, P, R, R, D, D, D, P], 'e2-e4, the C47 answers from its book; the knight g1 picked')
    shot('4_black', [S.HAND], '+ at the start: you play black, the board turned, the C47 opens')
    # two players: the fool's mate, f2-f3 e7-e5 g2-g4 Qd8-h4#
    shot('5_mate', [TWO, R, P, U, P, L, U, U, U, U, P, D, D, P, R, R, D, D, D, P, U, U, P,
                    L, L, L, U, U, U, U, P, R, R, R, R, D, D, D, D, P], 'two players: the fool\'s mate, CHECKMATE')
    shot('6_crazy', [S.LEVEL, S.LEVEL, P, U, U, P], 'level CRAZY (1 1): the face by the title')
    shot('7_ask960', [DIV, 72, 73], '÷ 1 2: the number of the Chess960 position asked')
    shot('8_960', [DIV, 72, 73, 74, D, R, P, R, P], '÷ 1 2 3: Chess960 No 123; 2 6 5 6 5: castling O-O, the king onto its rook')


if __name__ == '__main__':
    main()
