"""book.py - the opening book of CHESS47: main lines of the usual openings, up to 10 plies each (SAN). The build
(tools/build_chess47.py) writes them into the marker REM ==== BOOK as the rows of the matrix OB (the moves as
from x 1000 + to, the squares of the 10 x 12 mailbox); the C47 plays from it while the game so far is the start of a
line (one of the lines that fit, at random), then it thinks.
  lines()      the lines as move codes (checked legal with python-chess)
  candidates(history)   the book moves after a list of move codes"""
LINES = [
    'e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7',          # Ruy Lopez
    'e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d4 exd4',          # Italian
    'e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 d4 d5',          # Petrov
    'e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6',          # Sicilian, Najdorf
    'e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5',         # Sicilian, Sveshnikov
    'e4 e6 d4 d5 Nc3 Nf6 Bg5 Be7 e5 Nfd7',           # French
    'e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5 Ng3 Bg6',         # Caro-Kann
    'e4 d5 exd5 Qxd5 Nc3 Qa5 d4 Nf6 Nf3 c6',         # Scandinavian
    'd4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O',            # Queen's Gambit Declined
    'd4 d5 c4 c6 Nf3 Nf6 Nc3 dxc4 a4 Bf5',           # Slav
    'd4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O',            # King's Indian
    'd4 Nf6 c4 e6 Nc3 Bb4 e3 O-O Bd3 d5',            # Nimzo-Indian
    'c4 e5 Nc3 Nf6 Nf3 Nc6 g3 d5 cxd5 Nxd5',         # English
    'Nf3 d5 g3 Nf6 Bg2 e6 O-O Be7 d3 O-O',           # Reti
]
WIDTH = 11                                           # the columns of OB: 10 moves and a 0


def code(uci):
    sq = lambda t: 10 * (int(t[1]) + 1) + 'abcdefgh'.index(t[0]) + 2
    return sq(uci[:2]) * 1000 + sq(uci[2:4])


def lines():
    import chess
    out = []
    for ln in LINES:
        b = chess.Board()
        row = []
        for san in ln.split():
            m = b.parse_san(san)
            row.append(code(m.uci()))
            b.push(m)
        out.append(row)
    return out


def candidates(history):
    n = len(history)
    return [row[n] for row in lines() if len(row) > n and row[:n] == list(history)]


def steps():
    """The steps of the marker REM ==== BOOK: OB (rows x 11, zeros) and its rows (INDEX "OB" set)."""
    L = lines()
    out = [str(len(L)), str(WIDTH), 'NEWMAT', 'STO "OB"', 'DROP', 'INDEX "OB"']
    for r, row in enumerate(L):
        out += [str(r + 1), '1', 'STOIJ', 'DROP', 'DROP']
        for c in row:
            out += [str(c), 'STOSEQ', 'DROP']
    return out
