# Chess 47: working rules

- Work on a new branch; Victor creates and merges the PRs. Never force-push or rewrite history.
- Commit author: "Victor Valdes" <valdesvj@users.noreply.github.com>.
- Never commit binaries (.p47 files made by rejig).
- Edit the program in programs_rem/CHESS47.txt (commented source), then run python3 tools/build_chess47.py:
  it writes programs/, build/ and listings/ (and build/forum/). Never edit those by hand.
- The build fills the marker lines REM ==== GLYPHS and FACE from python/layout.py (the piece glyphs, the crazy face)
  and BOOK, BOOKN from python/book.py (the opening book): change them there.
- STRUCT as Elements 47: IF / ELSE / ENDIF, DO / WHILE / ENDDO, indented, no numbers in the source; a test
  right before IF / WHILE; never a test before ELSE, ENDIF, DO, ENDDO. CHESS47 is for the C47 / R47 / DM42n
  (255 IF / DO a program), not the old DM42. Named labels LBL :NAME: (1-7 letters or digits).
- The engine has a twin: python/chess47ref.py is the same algorithm step for step (the same moves in the same
  order, the same scores). A change to the engine goes in both; tests/test_chess47.py compares them.
- Text on the C47 screen: ATEXT in GRFNT 21 (GRFNT 10 for the small text). Restore GRFNT 20 and GRMOD 0 before
  the program ends. GRMOD and GRFNT take X: write `3 GRMOD`. AGRAPH words always through SINT.
- Key waits: DO / 0 / PAUSE 10 / KEY? 98 / XEQ :CLOCK: / X≠0? / WHILE / ENDDO (the clock each second). R-CLR with a count (20.79, then R99).
- Only commands already run on a C47 in Almanac 47, Elements 47, Zones 47 or Logic 47 (the bitwise ones AND OR NOT
  XOR BS?), except →REAL: say so in the README until Victor has run it; a new command: ask Victor to try it.
- CHESS47 runs in UNSIGN (its words use the top bit: keys 2^32, glyphs 2^24, knights 2^64) and gives the user's mode
  back (R.09, read with 1 SINT NOT →REAL at WSIZE 8). c47sim refuses SINT out of range and STOEL of a short integer
  (→REAL first) as the C47 (marked chess47).
- Check every change in the simulator (python3 python/chess47sim.py writes docs/*.png) and with
  python3 tests/test_chess47.py; the engine's play with python3 tools/match47.py (docs/MATCHES.md).
- python/c47sim.py, stdfont.py, tinyfont.py come from Almanac 47 (the bitwise block from Logic 47): a fix is
  made there first, then copied here.
- Work in one repository at a time (this one); the other 47 repositories are for reference only.
- Ask before anything that can't be undone. Pull requests only for chess47.
