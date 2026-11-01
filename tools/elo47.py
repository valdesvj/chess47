#!/usr/bin/env python3
"""elo47.py - the rating of CHESS47's engine: matches against Stockfish at fixed strengths (UCI_LimitStrength, UCI_Elo),
every move refereed by python-chess, and the rating that best explains the results (maximum likelihood, with its 95 %
interval).

The engine is python/chess47ref.py, the twin of CHESS47: the same moves in the same positions as the calculator (the
tests compare them), so a game takes seconds here instead of an hour on the C47. It plays as the C47 does: its opening
book first (book.py, at random among the lines that fit), then the search at the level asked (2 by default); a
promotion is always a queen. The games alternate the colours.

    pip install chess            (and Stockfish: pacman -S stockfish, or --stockfish /path/to/stockfish)
    python3 tools/elo47.py                         20 games against each of 1320 and 1400 -> docs/ELO.md
    python3 tools/elo47.py --games 20 --elos 1320,1450 --time 0.5 --level 2 --seed 1

What the number means: Stockfish's UCI_Elo is calibrated on a blitz scale of engine games (CCRL 40/4, at about 120 s
+ 1 s a game), not on FIDE ratings of people; at shorter times a limited Stockfish plays below its setting, so give
it --time 0.5 or more (seconds a move). 1320 is the lowest Stockfish 16 accepts: an engine far below it scores almost
nothing and the estimate becomes a bound ("below ..."). More games make the interval narrower (about +-200 with 40
games, +-100 with 160). A game is a draw at the rules' draws (threefold repetition, 50 moves, no mating material) or
after --maxply plies.
The games are written to docs/ELO_games.pgn, the results and the estimate to docs/ELO.md."""
import argparse, math, os, random, shutil, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import chess                                                     # noqa: E402
import chess.engine                                              # noqa: E402
import chess.pgn                                                 # noqa: E402
import book                                                      # noqa: E402
import chess47ref as R                                           # noqa: E402


def sq(s):
    """A square of the mailbox -> python-chess."""
    return chess.square((s - 1) % 10 - 1, (s - 1) // 10 - 2)


def mb(q):
    return 10 * (chess.square_rank(q) + 2) + chess.square_file(q) + 2


def chess47_move(b, history, level, rnd):
    """CHESS47's move in the position b: the book (normal chess, the first 10 plies, the lines that fit), else the
    twin's search at the level (0: CRAZY, a random legal move)."""
    p = R.Pos.fen(b.fen())
    legal = p.legal()
    if history is not None and len(history) < 10:
        cands = [m for m in book.candidates(history) if m in legal]
        if cands:
            return rnd.choice(cands)
    if level == 0:
        return rnd.choice(legal)
    m, v, nodes = p.search(level)
    return m


def to_move(b, m):
    f, t = sq(m // 1000), sq(m % 1000)
    piece = b.piece_at(f)
    promo = chess.QUEEN if piece and piece.piece_type == chess.PAWN and chess.square_rank(t) in (0, 7) else None
    return chess.Move(f, t, promotion=promo)


def play(engine, elo, chess47_white, level, secs, maxply, rnd):
    """One game: the result for CHESS47 (1, 0.5, 0), its reason, the game (PGN)."""
    engine.configure({'UCI_LimitStrength': True, 'UCI_Elo': elo})
    b = chess.Board()
    history = []                                                 # the moves as CHESS47 codes (the book's)
    while not b.is_game_over(claim_draw=True) and b.ply() < maxply:
        if (b.turn == chess.WHITE) == chess47_white:
            mv = to_move(b, chess47_move(b, history, level, rnd))
            if mv not in b.legal_moves:
                raise RuntimeError('CHESS47 played an illegal move %s in %s' % (mv.uci(), b.fen()))
        else:
            mv = engine.play(b, chess.engine.Limit(time=secs)).move
        if history is not None:
            history.append(mb(mv.from_square) * 1000 + mb(mv.to_square))
            if len(history) > 10:
                history = None
        b.push(mv)
    if b.ply() >= maxply and not b.is_game_over(claim_draw=True):
        result, why = '1/2-1/2', 'draw after %d plies' % maxply
    else:
        result = b.result(claim_draw=True)
        why = b.outcome(claim_draw=True).termination.name.lower().replace('_', ' ')
    score = {'1-0': 1.0, '0-1': 0.0, '1/2-1/2': 0.5}[result]
    if not chess47_white:
        score = 1 - score
    g = chess.pgn.Game.from_board(b)
    g.headers.update({'Event': 'CHESS47 level %d against Stockfish %d' % (level, elo),
                      'White': 'CHESS47 L%d' % level if chess47_white else 'Stockfish %d' % elo,
                      'Black': 'Stockfish %d' % elo if chess47_white else 'CHESS47 L%d' % level,
                      'Result': result, 'Termination': why})
    return score, why, g, b.ply()


def estimate(games):
    """The rating R that makes the expected score equal to the score (maximum likelihood; each game's expectation
    1 / (1 + 10^((opponent - R) / 400))), and its 95 % interval; None when the score is 0 or all (a bound only)."""
    total = sum(s for e, s in games)
    if total == 0 or total == len(games):
        return None
    lo, hi = -1000.0, 5000.0
    for _ in range(100):
        r = (lo + hi) / 2
        if sum(s - 1 / (1 + 10 ** ((e - r) / 400)) for e, s in games) > 0:
            lo = r
        else:
            hi = r
    info = sum((math.log(10) / 400) ** 2 * x * (1 - x) for x in (1 / (1 + 10 ** ((e - r) / 400)) for e, s in games))
    return r, 1.96 / math.sqrt(info)


def main():
    ap = argparse.ArgumentParser(description='the rating of CHESS47 against Stockfish at fixed strengths')
    ap.add_argument('--games', type=int, default=20, help='games against each strength (the colours alternate)')
    ap.add_argument('--elos', default='1320,1400', help="Stockfish's UCI_Elo settings (1320 the lowest)")
    ap.add_argument('--time', type=float, default=0.5, help="Stockfish's time a move, seconds")
    ap.add_argument('--level', type=int, default=2, help="CHESS47's level: 2, 1 or 0 (CRAZY)")
    ap.add_argument('--maxply', type=int, default=300, help='a draw after so many plies')
    ap.add_argument('--seed', type=int, default=47, help='the book and CRAZY choices (Stockfish varies anyway)')
    ap.add_argument('--stockfish', default=shutil.which('stockfish') or '/usr/games/stockfish')
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'ELO.md'))
    a = ap.parse_args()
    elos = [int(e) for e in a.elos.split(',')]
    rnd = random.Random(a.seed)
    engine = chess.engine.SimpleEngine.popen_uci(a.stockfish)
    name = engine.id.get('name', 'Stockfish')
    games, rows, pgns = [], [], []
    t0 = time.time()
    try:
        for elo in elos:
            score = 0.0
            for g in range(a.games):
                white = g % 2 == 0
                s, why, pgn, plies = play(engine, elo, white, a.level, a.time, a.maxply, rnd)
                games.append((elo, s))
                score += s
                pgns.append(pgn)
                print('Stockfish %d  game %2d  CHESS47 %s  %s  (%s, %d plies)' % (
                    elo, g + 1, 'white' if white else 'black', {1.0: 'won ', 0.5: 'draw', 0.0: 'lost'}[s], why, plies),
                    flush=True)
            rows.append((elo, score, a.games))
            print('  against %d: %.1f / %d' % (elo, score, a.games), flush=True)
    finally:
        engine.quit()
    est = estimate(games)
    total = sum(s for e, s in games)
    if est:
        r, ci = est
        verdict = 'about **%d** (95 %%: %d to %d)' % (round(r), round(r - ci), round(r + ci))
    elif total == 0:
        verdict = 'below the weakest setting: scored nothing against %d (below about %d)' % (min(elos), min(elos) - 400)
    else:
        verdict = 'above the strongest setting: won every game against %d' % max(elos)
    print('\nCHESS47 level %d: %.1f / %d against %s -> rating %s' % (a.level, total, len(games), name,
                                                                   verdict.replace('**', '')))
    md = ['# The rating of CHESS47', '',
          '`python3 tools/elo47.py %s`: CHESS47\'s engine (python/chess47ref.py, the same moves as the calculator) at '
          'level %d with its book, against %s with UCI_LimitStrength (%.1f s a move), refereed by python-chess. %s, '
          '%.0f min.' % (' '.join(sys.argv[1:]), a.level, name, a.time, time.strftime('%Y-%m-%d'), (time.time() - t0) / 60),
          '', '**Rating: %s**, on Stockfish\'s UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating).' % verdict, '',
          '| Stockfish UCI_Elo | CHESS47 scored | games | performance |', '|---|---|---|---|']
    for elo, score, n in rows:
        perf = estimate([(elo, s) for e, s in games if e == elo])
        md.append('| %d | %.1f | %d | %s |' % (elo, score, n, '%d' % round(perf[0]) if perf else
                                              ('< %d' % (elo - 400) if score == 0 else '> %d' % (elo + 400))))
    md += ['', 'The games: `docs/ELO_games.pgn`.']
    with open(a.out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    pgn = os.path.join(os.path.dirname(a.out), 'ELO_games.pgn')
    with open(pgn, 'w', encoding='utf-8') as fh:
        for g in pgns:
            print(g, file=fh, end='\n\n')
    print('-> %s and %s' % (a.out, pgn))


if __name__ == '__main__':
    main()
