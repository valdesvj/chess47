#!/usr/bin/env python3
"""influence47.py - what the influence maps are worth: CHESS47 level 2 with them (python/influence.py) against CHESS47
level 2 as it is (python/chess47ref.py, the twin of the calculator), every move refereed by python-chess.

Both are deterministic, so the games start from many openings, each played twice with the colours swapped: the book's
lines cut after 4 to 10 plies, and openings of 4 random plies (seeded). Then both search at level 2; a promotion is a
queen; a game is a draw at the rules' draws or after --maxply plies. The result: the score, the rating difference with
its 95 % interval (from the paired games), and the rating on the scale of docs/ELO.md (level 2: 981).
Also the cost a C47 port would pay: the leaves valued and the maps built a move.

    python3 tools/influence47.py                       -> docs/INFLUENCE.md
    python3 tools/influence47.py --random 40 --maxply 200 --variant leaf --jobs 2"""
import argparse, math, os, random, sys, time
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import chess                                                     # noqa: E402
import book                                                      # noqa: E402
import chess47ref as R                                           # noqa: E402
import influence as I                                            # noqa: E402

LEVEL2, LEVEL3 = 981, 1099                                       # docs/ELO.md (2026-11-01), CHESS47 levels 2 and 3


def sq(s):
    return chess.square((s - 1) % 10 - 1, (s - 1) // 10 - 2)


def to_move(b, m):
    f, t = sq(m // 1000), sq(m % 1000)
    piece = b.piece_at(f)
    promo = chess.QUEEN if piece and piece.piece_type == chess.PAWN and chess.square_rank(t) in (0, 7) else None
    return chess.Move(f, t, promotion=promo)


def openings(nrandom, seed):
    """The book's lines cut after 4-10 plies (each once), then nrandom openings of 4 random plies: lists of UCI."""
    out, seen = [], set()
    for line in book.lines():
        for n in range(4, 11, 2):
            ucis = tuple(chess.Move(sq(m // 1000), sq(m % 1000)).uci() for m in line[:n])
            if ucis not in seen:
                seen.add(ucis); out.append(list(ucis))
    rnd = random.Random(seed)
    want = len(out) + nrandom
    while len(out) < want:
        b = chess.Board()
        for _ in range(4):
            b.push(rnd.choice(list(b.legal_moves)))
        u = tuple(m.uci() for m in b.move_stack)
        if u not in seen and not b.is_game_over():
            seen.add(u); out.append(list(u))
    return out


def game(args):
    """One game from the opening: the score of the influence engine (1, 0.5, 0), the plies, its leaves and maps."""
    ucis, inf_white, maxply, variant, weights, opp = args
    I.WEIGHTS.update(weights)
    b = chess.Board()
    for u in ucis:
        b.push_uci(u)
    leaves = maps = moves = 0
    while not b.is_game_over(claim_draw=True) and b.ply() < maxply:
        mine = (b.turn == chess.WHITE) == inf_white
        if mine:
            p = I.InfPos.fen(b.fen())
            p.variant = variant
            before = I.InfPos.maps_built
            m, v, n = p.search(2)
            leaves += n; maps += I.InfPos.maps_built - before; moves += 1
        else:
            q = R.Pos.fen(b.fen())
            q.budget = None
            m, v, n = q.search(opp)
        mv = to_move(b, m)
        if mv not in b.legal_moves:                    # an illegal move loses the game (counted apart)
            s = 0.0 if mine else 1.0
            return s, b.ply(), leaves, maps, moves, ('influence' if mine else 'twin', mv.uci(), b.fen())
        b.push(mv)
    if b.ply() >= maxply and not b.is_game_over(claim_draw=True):
        res = '1/2-1/2'
    else:
        res = b.result(claim_draw=True)
    s = {'1-0': 1.0, '0-1': 0.0, '1/2-1/2': 0.5}[res]
    return (s if inf_white else 1 - s), b.ply(), leaves, maps, moves, None


def elo(score):
    score = min(max(score, 1e-3), 1 - 1e-3)
    return -400 * math.log10(1 / score - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--random', type=int, default=40)
    ap.add_argument('--maxply', type=int, default=200)
    ap.add_argument('--seed', type=int, default=47)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--variant', default='leaf')
    ap.add_argument('--opp', type=int, default=2, help='the level of the plain twin (2, or 3: level 3 searched to the end)')
    ap.add_argument('--weights', default='', help='changes to influence.WEIGHTS, e.g. C_ALL=2,T_FORK=1')
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'INFLUENCE.md'))
    a = ap.parse_args()
    for kv in filter(None, a.weights.split(',')):
        k, v = kv.split('=')
        I.WEIGHTS[k] = float(v)
    ops = openings(a.random, a.seed)
    tasks = [(o, w, a.maxply, a.variant, dict(I.WEIGHTS), a.opp) for o in ops for w in (True, False)]
    t0 = time.time()
    with Pool(a.jobs) as pool:
        res = pool.map(game, tasks, chunksize=1)
    secs = time.time() - t0
    pairs = [res[i][0] + res[i + 1][0] for i in range(0, len(res), 2)]      # 0 .. 2 a pair
    n = len(res)
    score = sum(r[0] for r in res) / n
    wins = sum(1 for r in res if r[0] == 1); draws = sum(1 for r in res if r[0] == 0.5); losses = n - wins - draws
    mean = sum(pairs) / len(pairs) / 2
    sd = math.sqrt(sum((p / 2 - mean) ** 2 for p in pairs) / (len(pairs) - 1)) / math.sqrt(len(pairs))
    lo, hi = elo(mean - 1.96 * sd), elo(mean + 1.96 * sd)
    leaves = sum(r[2] for r in res); maps = sum(r[3] for r in res); moves = sum(r[4] for r in res)
    d = elo(score)
    lines = ['# The influence maps at level 2 (a Python test)', '',
             '`python3 tools/influence47.py --random %d --maxply %d --seed %d --variant %s`, %s, %d s.'
             % (a.random, a.maxply, a.seed, a.variant, time.strftime('%Y-%m-%d'), secs), '',
             'CHESS47 level 2 with the influence maps (python/influence.py, weights %s) against CHESS47 level 2 as it is '
             '(python/chess47ref.py) at level %d, %d openings each played with both colours, refereed by python-chess.'
             % (I.WEIGHTS, a.opp, len(ops)), '',
             '| games | wins | draws | losses | score | rating difference | 95 % | on docs/ELO.md\'s scale (the opponent) |',
             '|---|---|---|---|---|---|---|---|',
             '| %d | %d | %d | %d | %.1f %% | %+d | %+d to %+d | about %d (the opponent: %d) |'
             % (n, wins, draws, losses, 100 * score, d, lo, hi, (LEVEL2 if a.opp == 2 else LEVEL3) + d,
                (LEVEL2 if a.opp == 2 else LEVEL3)), '',
             'The cost on the C47: %.0f leaves valued a move; %.1f influence maps a move (both colours each: %d in %d moves); '
             'the plies a game: %.0f.' % (leaves / max(moves, 1), maps / max(moves, 1), maps, moves, sum(r[1] for r in res) / n), '',
             'Illegal moves (the game lost by the side that played it): %s.'
             % ('; '.join('%s %s in %s' % r[5] for r in res if r[5]) or 'none')]
    open(a.out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
