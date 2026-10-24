# Chess 47 Documentation

Screens, progress notes and parity references for the mini chess engine.

## Current status (skeleton + split screen)

- Board drawn with ATEXT + simple AGRAPH square outlines.
- Move list placeholder on the right side of the screen (split layout).
- Matrix `BD` holds the position (Micro-Max style codes).
- Stack / LASTx preserved, standby handled, clean exit.

Screens will be generated with the C47 simulator (c47sim from Almanac 47 or the official simulator) and placed here as PNG files.

## Planned parity checks

- Starting position board pixels vs reference.
- Move list text after a sequence of moves.
- Legal-move count for known positions (perft-style, shallow).
- Cross-check against independent Python chess logic.

See `tests/` for the parity tool skeleton.
