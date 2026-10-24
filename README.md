# Chess 47 ♟️

A mini chess engine for the **C47 / R47** RPN calculator firmware.

Matrix-based board representation, inspired by Micro-Max (H.G. Muller). Target: DM42n / C47 / R47 with STRUCT, ATEXT, GRFNT and simple AGRAPH. Planned 64-bit bitwise bitboards for move generation.

---

## Chess 47 (current build)

`CHESS` creates an 8×8 matrix `BD`, fills it with piece codes, draws a board (ATEXT pieces + simple AGRAPH square outlines) and a move-list panel on the right (split screen), then waits for a key. **0** ends cleanly.
Your stack and LASTx are kept. Standby is handled the same way as Elements 47.

| | C47 / R47 |
|---|---|
| File | `programs/CHESS47.txt` (commented copy in `programs_rem/`) |
| Needs | firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later (STRUCT, ATEXT, GRFNT, AGRAPH) |
| Memory | matrix `BD` and work registers |
| At the end (0) | matrix deleted, work registers cleared (R-CLR); **the user's stack and LASTx kept**; GRFNT 20 and GRMOD 0 restored |

**Status**

- [x] Repository, skeleton, Micro-Max-style encoding
- [x] ATEXT + simple AGRAPH board, split-screen move list placeholder
- [x] STRUCT, stack/LASTx preservation, standby, clean exit
- [x] docs/ and tests/ folders started (parity skeleton)
- [ ] Legal move generator (64-bit bitboards preferred)
- [ ] Material evaluation and shallow search
- [ ] Full AGRAPH piece glyphs and richer move list
- [ ] Simulator screens + pixel parity checks

Screens and progress notes: see `docs/`. Parity tool skeleton: `tests/test_chess47.py`. Pattern matches Almanac 47 / Elements 47 / Logic 47.

Further versions will be checked in the C47 simulator. References: C47 matrix AN0020, 64-bit bitwise (Logic 47), ATEXT/GRFNT/AGRAPH and STRUCT in recent firmware.

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community.
