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

## v0.1 on Victor's C47 (Nov 18, 2026)

| | what | microseconds a time |
|---|---|---|
| | the empty loop (DSE, WHILE) | 360 |
| A | `1 RCL R.02 STOIJ RCLEL` (1 × 120) | 1 630 |
| B | `RCL IND` global | 120 |
| C | `RCL IND` local, same level | 130 |
| D | `RCL R.05` | 110 |
| E | `XEQ` + `RTN` | 670 |

The subroutine reading the caller's R.05: **"Out of range"**, as the firmware's source says. A matrix read costs about
13 register reads, `XEQ`/`RTN` about 5-6: the simulator's equal steps hide both.

## v0.2: does the time grow with the matrix?

In the firmware (`src/c47/mathematics/matrix.c`, `callByIndexedMatrix`) every `STOIJ`, `RCLEL`, `STOEL`, `RCLSEQ`,
`STOSEQ` copies the whole indexed matrix into a new one (`convertReal34MatrixRegisterToReal34Matrix`), and a write
copies it back (`convertReal34MatrixToReal34MatrixRegister`), though `linkToRealMatrixRegister` (no copy) exists.
LOCT47 v0.2 (`build/dev-opt/LOCT47.txt`, about 2 minutes) times, 2 000 times each:

| | what |
|---|---|
| 1-3 | `RCLEL`, `STOIJ`, `STOEL` on 1 × 120 |
| 4-5 | `RCLEL`, `STOEL` on 14 × 120 (CHESS47 v0.7.0's BD) |
| 6-7 | `RCLEL`, `STOEL` on 23 × 120 (v0.6.0's BD) |
| 8 | `RCLSEQ` on 23 × 120 |
| 9 | `J+` on 23 × 120 |
| 10 | `INDEX` twice (a 1 × 1 matrix and the 23 × 120 one) |

If 4-7 cost clearly more than 1 and 3, the copy is the cost: then CHESS47 wants small matrices (the board apart), and
a merge request to c43 (link instead of copy in `callByIndexedMatrix`) would speed up every matrix program.
