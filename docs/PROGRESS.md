# Chess 47 Progress Log

Frequent notes so work is recoverable.

## 2026-10-24 — Split-screen skeleton

- Matrix `BD` (8×8) with Micro-Max piece codes.
- ATEXT pieces + simple AGRAPH square outlines.
- Right-side move-list panel placeholder (split screen).
- Full stack/LASTx preservation, standby detection, clean exit (matches Elements 47 / Logic 47 pattern).
- `docs/` and `tests/` folders created.
- `programs_rem/CHESS47.txt` kept in sync.
- Parity-test skeleton in `tests/test_chess47.py`.

## 2026-10-24 — Basic move input

- Key other than 0 now calls LBL 20.
- LBL 20 appends a dummy move string (" e2e4") to register 60 and redraws the board + move list.
- Prompt updated to "0 END  1 MOVE".
- Rem version synced.

## Next immediate steps

1. Replace dummy move with real algebraic input and board update.
2. Add first legal-move checks (pawns and knights).
3. Capture screens with c47sim and store in `docs/`.
4. Expand parity checks against known positions.

Pattern follows Almanac 47, Elements 47 and Logic 47: frequent notes, simulator parity, clean firmware style.
