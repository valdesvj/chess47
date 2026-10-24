# Chess 47 Development Notes

## Design goals

- Matrix-based board (`BD`, 8×8) using firmware matrix commands (NEWMAT, INDEX, STOIJ, RCLEL, STOSEQ).
- Display with ATEXT and GRFNT (recent firmware 00.109.05.00a0.ALPHA or later).
- STRUCT control flow (IF/DO/REPEAT) for clarity and speed on DM42n / R47.
- Full user-state preservation (stack, LASTx) and standby handling matching Elements 47 / Logic 47 / Almanac 47.
- Clean exit: delete matrix, clear work registers only, restore GRMOD / GRFNT.

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

## References

- C47 matrix application note AN0020 (Matrix and Vector).
- Firmware release notes for ATEXT, GRFNT, STRUCT (AN0007).
- Existing programs in almanac47, elements47, logic47, zones47 for stack, standby and matrix patterns.

## Next steps

1. Legal move generator (piece type + direction vectors, preferably also stored in a small matrix).
2. Material evaluation.
3. 1-ply then 2-ply search.
4. Simulator tests (Python C47 simulator from Almanac 47).

All changes are validated by the author before release.
