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
The games are written to docs/ELO_games.pgn, the results and the estimate to docs/ELO.md.

    python3 tools/elo47.py --ladder [--games 8]     the ladder (recommended): CHESS47 is far below Stockfish's lowest
setting, so a direct match says little. Every player meets every other (--games each pair, the colours alternate):
Stockfish 1320 (the anchor, its rating fixed), Stockfish at Skill Level 0 (0.1 s a move, depth 3, depth 1), CHESS47
levels 3, 2 and 1, and a plain material player (two plies, python-chess, random among equals: tools/match47.py's). One
fit rates them all (Bradley-Terry, as Ordo / BayesElo; a half draw of prior between each pair keeps a clean sweep
finite), and the 95 % interval comes from 200 refits on resampled games (bootstrap)."""
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


VALS = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 320, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def material_move(b, rnd):
    """tools/match47.py's opponent: two plies, material only, the moves of equal value at random."""
    def ev(bb):
        return sum(VALS[p.piece_type] * (1 if p.color == bb.turn else -1) for p in bb.piece_map().values())
    best, cands = -10 ** 9, []
    for m in b.legal_moves:
        if m.promotion and m.promotion != chess.QUEEN:
            continue
        b.push(m)
        if b.is_checkmate():
            worst = 10 ** 6
        else:
            worst = 10 ** 9
            for r in b.legal_moves:
                b.push(r)
                worst = min(worst, -ev(b) if not b.is_checkmate() else -10 ** 6)
                b.pop()
            if worst == 10 ** 9:
                worst = 0
        b.pop()
        if worst > best:
            best, cands = worst, [m]
        elif worst == best:
            cands.append(m)
    return rnd.choice(cands)


LADDER = [('Stockfish 1320', ('sf', {'UCI_LimitStrength': True, 'UCI_Elo': 1320}, None)),
          ('Stockfish skill 0, 0.1 s', ('sf', {'UCI_LimitStrength': False, 'Skill Level': 0}, 0.1)),
          ('Stockfish skill 0, depth 3', ('sf', {'UCI_LimitStrength': False, 'Skill Level': 0}, 'd3')),
          ('Stockfish skill 0, depth 1', ('sf', {'UCI_LimitStrength': False, 'Skill Level': 0}, 'd1')),
          ('CHESS47 level 3', ('c47', 3)), ('CHESS47 level 3, 60 s', ('c47', 3, 750)), ('CHESS47 level 2', ('c47', 2)), ('CHESS47 level 1', ('c47', 1)),
          ('material 2 plies', ('mat',))]


def ladder_game(engine, white, black, secs, maxply, rnd):
    """One game between two ladder players: the result for white (1, 0.5, 0), the reason, the PGN, the plies."""
    b = chess.Board()
    hist = {chess.WHITE: [], chess.BLACK: []}                    # the book's history, for a CHESS47 side
    players = {chess.WHITE: white, chess.BLACK: black}
    while not b.is_game_over(claim_draw=True) and b.ply() < maxply:
        name, spec = players[b.turn]
        if spec[0] == 'c47':
            h = hist[b.turn] if hist[b.turn] is not None and len(b.move_stack) <= 10 else None
            if h is not None:
                h[:] = [mb(m.from_square) * 1000 + mb(m.to_square) for m in b.move_stack]
            R.Pos.budget = spec[2] if len(spec) > 2 else None      # level 3 on the C47: about 750 answers in 60 s
            mv = to_move(b, chess47_move(b, h, spec[1], rnd))
            R.Pos.budget = None
            if mv not in b.legal_moves:
                raise RuntimeError('CHESS47 played an illegal move %s in %s' % (mv.uci(), b.fen()))
        elif spec[0] == 'mat':
            mv = material_move(b, rnd)
        else:
            engine.configure(spec[1])
            lim = spec[2]
            limit = (chess.engine.Limit(time=secs) if lim is None else chess.engine.Limit(time=lim) if
                     isinstance(lim, float) else chess.engine.Limit(depth=int(lim[1:])))
            mv = engine.play(b, limit).move
        b.push(mv)
    if b.is_game_over(claim_draw=True):
        result = b.result(claim_draw=True)
        why = b.outcome(claim_draw=True).termination.name.lower().replace('_', ' ')
    else:
        result, why = '1/2-1/2', 'draw after %d plies' % maxply
    g = chess.pgn.Game.from_board(b)
    g.headers.update({'Event': 'CHESS47 rating ladder', 'White': white[0], 'Black': black[0], 'Result': result,
                      'Termination': why})
    return {'1-0': 1.0, '0-1': 0.0, '1/2-1/2': 0.5}[result], why, g, b.ply()


def fit(n, games, anchor=0, anchor_elo=1320.0, prior=0.5):
    """Bradley-Terry ratings of n players from games (i, j, score of i), player anchor fixed at anchor_elo; a prior
    of a half draw between each pair that met keeps a clean sweep finite."""
    pairs = {(min(i, j), max(i, j)) for i, j, s in games}
    data = list(games) + ([(i, j, 0.5) for i, j in sorted(pairs)] if prior else [])
    r = [anchor_elo] * n
    k = math.log(10) / 400
    for it in range(2000):
        grad, hess = [0.0] * n, [0.0] * n
        for idx, (i, j, s) in enumerate(data):
            wt = prior if idx >= len(games) else 1.0
            e = 1 / (1 + 10 ** ((r[j] - r[i]) / 400))
            grad[i] += wt * (s - e)
            grad[j] -= wt * (s - e)
            hess[i] += wt * k * e * (1 - e)
            hess[j] += wt * k * e * (1 - e)
        step = 0.0
        for p in range(n):
            if p != anchor and hess[p] > 0:
                d = max(-200.0, min(200.0, grad[p] / hess[p]))
                r[p] += d
                step = max(step, abs(d))
        if step < 0.01:
            break
    return r


def ladder(a):
    rnd = random.Random(a.seed)
    engine = chess.engine.SimpleEngine.popen_uci(a.stockfish)
    sfname = engine.id.get('name', 'Stockfish')
    n = len(LADDER)
    games, pgns, t0 = [], [], time.time()
    try:
        for i in range(n):
            for j in range(i + 1, n):
                sc = 0.0
                for g in range(a.games):
                    wi = g % 2 == 0
                    w, bl = (LADDER[i], LADDER[j]) if wi else (LADDER[j], LADDER[i])
                    s, why, pgn, plies = ladder_game(engine, w, bl, a.time, a.maxply, rnd)
                    si = s if wi else 1 - s
                    games.append((i, j, si))
                    sc += si
                    pgns.append(pgn)
                print('%-28s - %-28s %4.1f - %4.1f' % (LADDER[i][0], LADDER[j][0], sc, a.games - sc), flush=True)
    finally:
        engine.quit()
    r = fit(n, games)
    boot = []
    brnd = random.Random(1)
    for _ in range(200):
        boot.append(fit(n, [games[brnd.randrange(len(games))] for _ in games]))
    ci = []
    for p in range(n):
        v = sorted(b[p] for b in boot)
        ci.append((v[5], v[194]))
    print()
    order = sorted(range(n), key=lambda p: -r[p])
    for p in order:
        print('%-28s %5d   (95 %%: %d to %d)' % (LADDER[p][0], round(r[p]), round(ci[p][0]), round(ci[p][1])))
    c2 = [p for p in range(n) if LADDER[p][0] == 'CHESS47 level 2'][0]
    c3 = [p for p in range(n) if LADDER[p][0] == 'CHESS47 level 3'][0]
    md = ['# The rating of CHESS47', '',
          '`python3 tools/elo47.py %s`: a ladder, every player against every other (%d games a pair, the colours '
          'alternating), refereed by python-chess; %s; CHESS47 is python/chess47ref.py (the same moves as the '
          'calculator) with its book. One fit rates them all with Stockfish 1320 fixed (Bradley-Terry); the intervals '
          'from 200 refits on resampled games. %s, %.0f min.' % (' '.join(sys.argv[1:]), a.games, sfname,
                                                                time.strftime('%Y-%m-%d'), (time.time() - t0) / 60),
          '', '**CHESS47 level 3: about %d** (95 %%: %d to %d), **level 2: about %d** (95 %%: %d to %d), on Stockfish\'s '
          'UCI_Elo scale (engine blitz, CCRL-like; not a FIDE rating). Level 3 as searched to the end (on the C47 its '
          'time budget can cut it short: then it plays its level-2 move).' % (
              round(r[c3]), round(ci[c3][0]), round(ci[c3][1]), round(r[c2]), round(ci[c2][0]), round(ci[c2][1])), '',
          '| player | rating | 95 % |', '|---|---|---|']
    for p in order:
        md.append('| %s | %d | %d to %d |' % (LADDER[p][0], round(r[p]), round(ci[p][0]), round(ci[p][1])))
    md += ['', '| %s | %s |' % ('', ' | '.join(LADDER[q][0] for q in range(n))), '|---|' + '---|' * n]
    for p in range(n):
        cells = []
        for q in range(n):
            if p == q:
                cells.append('-')
                continue
            s = sum(si if i == p else 1 - si for i, j, si in games if {i, j} == {p, q})
            cells.append('%g' % s)
        md.append('| %s | %s |' % (LADDER[p][0], ' | '.join(cells)))
    md += ['', 'The score of the row\'s player against the column\'s (%d games each). The games: '
           '`docs/ELO_games.pgn`.' % a.games]
    with open(a.out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    pgn = os.path.join(os.path.dirname(a.out), 'ELO_games.pgn')
    with open(pgn, 'w', encoding='utf-8') as fh:
        for g in pgns:
            print(g, file=fh, end='\n\n')
    print('-> %s and %s' % (a.out, pgn))


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
    ap.add_argument('--ladder', action='store_true', help='the ladder of weaker players (recommended)')
    a = ap.parse_args()
    if a.ladder:
        if '--games' not in sys.argv:
            a.games = 8
        return ladder(a)
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
        verdict = 'about %d (95 %%: %d to %d)' % (round(r), round(r - ci), round(r + ci))
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
