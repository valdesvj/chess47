# AI Assistance Policy

## How this project uses AI

This project was **developed with the help of AI** as a cooperation: Grok for the first skeleton, Claude (by Anthropic) for the engine of v0.1.0. AI assisted with brainstorming, program structure, RPN listing format and documentation, but I reviewed all output, will validate results against a reference implementation and the C47 simulator, and take full responsibility for the work and any mistakes.

## Responsible use

- ✅ **I check the results** — Move generation and evaluation will be validated in the C47 simulator against an independent Python reference (same approach as Logic 47 and Elements 47)
- ✅ **I maintain domain expertise** — I guide the design decisions: the board matrix, the keys, what is shown, and the depth of search
- ✅ **I take full responsibility** — The work is mine; any errors are mine to fix
- ✅ **I'm transparent** — This file documents how AI was used

## Testing & Validation

- Simulator tests: the C47 program in the Python C47 simulator (from Almanac 47) against `python/chess47ref.py`, the same engine in Python: every move generated, every search, a whole game (tests/test_chess47.py)
- The reference's move generator checked against the published perft counts
- To be tested on real C47 / R47 hardware before each release

## License

This does not affect the GNU GPL-3.0 license. All code remains open-source and fully accessible.

---

*For more details, see the development notes as they are added.*
