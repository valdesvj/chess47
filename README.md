# Chess 47 ♟️

A mini chess engine for the **C47 / R47** RPN calculator firmware.

Matrix-based board representation, inspired by Micro-Max (H.G. Muller). Target: DM42n / C47 / R47 with STRUCT, ATEXT and GRFNT. Planned use of 64-bit bitwise operations for bitboard-style move generation (same technique as Logic 47).

---

## Chess 47 (current skeleton)

`CHESS` creates an 8×8 matrix `BD`, fills it with Micro-Max-style piece codes, draws a text board with ATEXT / GRFNT, and waits for a key. **0** ends cleanly.
Your stack and LASTx are kept. Standby is handled the same way as Elements 47.

| | C47 / R47 |
|---|---|
| File | `programs/CHESS47.txt` |
| Needs | firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later (STRUCT, ATEXT, GRFNT) |
| Memory | matrix `BD` and work registers |
| At the end (0) | matrix deleted, work registers cleared (R-CLR); **the user's stack and LASTx kept**; GRFNT 20 and GRMOD 0 restored |

**Status**

- [x] Repository and initial skeleton
- [x] Micro-Max-style piece encoding (1–12) and ATEXT display
- [x] STRUCT control flow, stack/LASTx preservation, standby detection, matrix cleanup
- [ ] Legal move generator (prefer 64-bit bitboards + bitwise ops)
- [ ] Material evaluation
- [ ] Shallow search (1–2 ply)
- [ ] Improved / graphic display

Further versions will be checked in the C47 simulator (same approach as Almanac 47, Elements 47 and Logic 47). References: C47 matrix app note AN0020, 64-bit bitwise (as in Logic 47), ATEXT/GRFNT and STRUCT in recent firmware. Advanced functions (EIGEN, XFCNS) available for experimental use.

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community.
