# Chess 47 ♟️

A mini chess engine for the **C47 / R47** RPN calculator firmware.

Matrix-based board representation, inspired by Micro-Max (H.G. Muller). Target: DM42n / C47 / R47 with STRUCT, ATEXT and GRFNT.

---

## Chess 47 (initial skeleton)

`CHESS` sets up an 8×8 board matrix `BD`, displays a simple text board, and waits for a key. **0** ends cleanly.
Your stack and LASTx are kept.

| | C47 / R47 |
|---|---|
| File | `programs/CHESS47.txt` |
| Needs | firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later (STRUCT, ATEXT, GRFNT) |
| Memory | matrix `BD` and a few work registers |
| At the end (0) | work registers cleared; **the user's stack and LASTx kept** |

**Status**

- [x] Repository and initial skeleton
- [ ] Proper Micro-Max-style piece encoding
- [ ] Legal move generator
- [ ] Material evaluation
- [ ] Shallow search (1–2 ply)
- [ ] Improved display
- [ ] Full stack preservation and standby handling (same pattern as Elements 47 / Logic 47)

Tested so far only as a skeleton. Further versions will be checked in the C47 simulator (same approach as Almanac 47, Elements 47 and Logic 47).

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community.
