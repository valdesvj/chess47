# Chess 47 Development Notes

## Design goals

- Matrix-based board (`BD`, 8×8) using firmware matrix commands (NEWMAT, INDEX, STOIJ, RCLEL, STOSEQ) for the primary representation and display.
- Alternative or complementary **64-bit bitboard** representation using the firmware's 64-bit integer mode and bitwise commands (AND, OR, XOR, NOT, BS?, BC?, shifts). One 64-bit word per piece type or occupancy — the same technique used in Logic 47 for whole-table evaluation. This is the natural high-speed path for move generation.
- Display with ATEXT and GRFNT (firmware 00.109.05.00a0.ALPHA or later).
- STRUCT control flow (IF/DO/REPEAT) for clarity and speed on DM42n / R47.
- Full user-state preservation (stack, LASTx) and standby handling matching Elements 47 / Logic 47 / Almanac 47.
- Clean exit: delete matrices, clear work registers only, restore GRMOD / GRFNT.
- Optional use of advanced functions where they help: EIGVAL / EIGVEC for experimental matrix-based evaluation terms, XFCNS for any high-precision intermediate calculations if needed.

## Piece encoding (Micro-Max inspired)

Integer codes in the matrix:

- 0 empty
- 1 white pawn, 2 black pawn
- 3 white knight, 4 black knight
- 5 white bishop, 6 black bishop
- 7 white rook, 8 black rook
- 9 white queen, 10 black queen
- 11 white king, 12 black king

Display maps these to ASCII characters (P/p, N/n, …).

Bitboards can be derived from the matrix (or maintained in parallel) for fast attack generation.

## References

- C47 matrix application note AN0020 (Matrix and Vector) and EIGEN functions.
- Firmware support for 64-bit integers and bitwise operations (used successfully in Logic 47).
- ATEXT / GRFNT and STRUCT (AN0007) in recent firmware.
- Existing programs in almanac47, elements47, logic47, zones47 for stack, standby, matrix and bitwise patterns.

## Next steps

1. Legal move generator — preferably bitboard-based (64-bit bitwise) with a matrix fallback or hybrid for display.
2. Material evaluation (simple integer or matrix sum).
3. 1-ply then 2-ply search.
4. Simulator tests (Python C47 simulator from Almanac 47) plus cross-check of bitboard results.

All changes are validated by the author before release.
