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

## Next immediate steps

1. Wire basic move input and update the move-list string on the right.
2. Add first legal-move checks (pawns and knights as starting point).
3. Capture screens with c47sim and store in `docs/`.
4. Expand parity checks against known positions.

Pattern follows Almanac 47, Elements 47 and Logic 47: frequent notes, simulator parity, clean firmware style.
