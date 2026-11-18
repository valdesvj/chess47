# dev-opt: the test for the board in local registers (branch claude/chess47-dev-opt)

The plan (Step 4 of the optimisation, Nov 18, 2026): keep CHESS47's board in local registers and read it with
`RCL IND` (one step a square instead of `1 RCL nn STOIJ RCLEL`, four).

**What the firmware says.** In the C47 source (`src/c47/programming/lblGtoXeq.c`, `fnExecute`) every `XEQ` of a
running program starts a new subroutine level with no local registers (`currentNumberOfLocalRegisters = 0`), and
`RCL IND` of 112 + n reaches R.nn of the running level only (`registers.c`, `isValidIndirectRegisterParam`). `LocR`
stops at 99 (`allocateLocalRegisters`), and the mailbox has 120 squares. CHESS47 reads its board in routines it calls
with `XEQ` (GEN, ATT, MAKE, DELTA), so they cannot see CHESS47's local registers: the plan cannot work as it stands.
The simulator (`python/c47sim.py`) already keeps local registers per level; `tests/test_devopt.py` checks it.

**LOCT47**, to run on the C47 (`build/dev-opt/LOCT47.txt`, convert with rejig; source `programs_rem/LOCT47.txt`,
built by `python3 tools/build_devopt.py`). It takes about a minute and shows, in microseconds a time (10 000 times
each, the empty loop taken off):

| | what | CHESS47 uses it |
|---|---|---|
| A | a matrix element, `1 RCL R.02 STOIJ RCLEL` | every board read |
| B | `RCL IND` of a global register | (the knight and direction offsets) |
| C | `RCL IND` of a local register of the same level | the plan |
| D | `RCL R.05` | |
| E | `XEQ` and `RTN` of an empty routine | about 6 400 calls in 5 positions |

Then, after a key, a routine called with `XEQ` reads R.05: **an error there (local register .05 not defined) confirms
the firmware's rule.** "SUBROUTINE SAW R.05 = 47" instead would mean it can, and the plan is open again.

Please send the five numbers. They tell what a simulator step is worth on the calculator: if A costs about four
times B or C, or E is much more than two plain steps (the firmware allocates and frees memory at each `XEQ`), the
next speed work goes to inlining calls and keeping values in registers rather than matrix reads.
