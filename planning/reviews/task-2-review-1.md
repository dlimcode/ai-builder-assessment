## Review of 3d59fa7, "test(checker): add golden set before any code"

**Outcome:** the commit does what tasks 1 and 2 ask, and the suite fails only because `check_citations` is missing. I found one Medium gap: a checker that skips `realpath(root)` passes every test. The rest are Lows.

**What matches tasks 1 and 2** (each checked by script or by running it):
- **Export is faithful.** All 7 files in `.review/3d59fa7` are byte-identical to `git show 3d59fa7:<path>` (`cmp`).
- **Fixtures match 01 section 5 byte for byte.** `notes.md` and `data/plan.txt` were rebuilt from 01's blocks with the line numbers stripped, and compared. `empty.md` is 0 bytes, `bin.dat` is `\377\376\375`, and `fixtures-evil/x.md` is `x\n`.
- **Task 1 done-check** prints `9`, `33`, `3`, `ok`.
- **The table** is one list, `GOLDEN`, with 33 rows. Row by row against 01's table:
  - Text and verdict agree on rows 1-26 and H1-H4.
  - The only verdict difference is H3: "file missing" on the repo copy, which README task 2 asks for.
  - The "found at" column agrees on every row that is not "holds".
  - Row 23 uses U+201C and U+201D.
  - `report.md` lines equal the `GOLDEN` texts, and `tests/test_check_citations.py:133` checks this.
- **Summary** counts from `GOLDEN`: 10 holds, 1 line only, 2 not checked, 20 red, 33 in all. This matches `tests/test_check_citations.py:57`.
- **Exit codes:** exit 1 (`:179`), exit 0 (`:191`), and exit 2 for a folder argument (`:194`), a missing report (`:197`), a bad flag (`:200`) and no arguments (`:203`).
- **H3:** temp copy of both folders plus a symlink (`:152-157`).

**Rows recomputed by hand from notes.md, all correct:**
- Row 3: line 4 plus line 5 joined does not hold the words; they are only on line 3.
- Row 10: the span starts on line 6.
- Row 12: "side entrance" is only on line 5.
- Rows 15, 16, 17: found at lines 3, 1 and 7.
- Row 20: found at lines 1 and 3.
- H4: "x" appears nowhere in notes.md, so found is `[]`.
- H5: `commonpath` gives `.../tests`, which is not the root, so it is refused. A `startswith` checker would say "holds", because x.md line 1 is `x`, so this row catches that bug.

### F1. Medium. A root reached through a symlink is never checked, so dropping `realpath(root)` passes every test
- **Evidence:**
  - `tests/test_check_citations.py:153 "self.tmp = tempfile.mkdtemp(prefix="cc-golden-")"`
  - `tests/test_check_citations.py:168-171 "self.assertEqual(out.returncode, 1, out.stderr)" … "self.assertIn("refused: outside root", line[0])"`
- **Why it matters:** on this Mac `tempfile.gettempdir()` is `/tmp/claude-501`, which resolves to `/private/tmp/claude-501`. So the copy's root sits behind a symlink.
- **Failure path:**
  1. The checker resolves the target but not the root.
  2. `commonpath(["/tmp/claude-501/cc-golden-…/fixtures", "/private/tmp/…/notes.md"])` is `/`, so every reference in the copy is refused.
  3. The run still exits 1, and the `link-out.md:1` line still says refused, so `:164` and `:166-171` pass.
  4. GoldenTests use the repo path, which has no symlink, so they pass too.
  5. In real use, any `--root` through a symlink (`/tmp`, a symlinked checkout) turns every reference into "refused: outside root".
- **Fix:** in `test_report_run_in_the_copy`, also check every `SUMMARY` part on the last line. The counts in the copy are the same, because H3 only moves from one red verdict ("file missing") to another ("refused").

### F2. Low. The summary check matches substrings, so "11 line only" passes as "1 line only"
- **Evidence:**
  - `tests/test_check_citations.py:57 "SUMMARY = ("33 references", "10 holds", "1 line only", "20 red", "2 not checked")"`
  - `tests/test_check_citations.py:182 "self.assertIn(part, last)"`
- **Failure path:** a checker printing `33 references, 10 holds, 11 line only, 20 red, 2 not checked` passes, even though its counts sum to 43, not 33. "12 not checked" and "120 red" would pass the same way.
- **Fix:** use a word-boundary regex, or check the counts sum to the total.
- **Mitigation:** `test_rows` already fixes each row's verdict, so this only bites a wrong counting step in the summary.

### F3. Low. Three behaviours 01 asks for are not tested
1. **First three places only** (01 section 3, "list every place they are (first three)"). No row has more than 3 places, so a checker that lists all of them passes.
2. **H3's file is never opened** (`planning/01-prior-art-and-formats.md:135 "For H3, the file must never be opened"`). The verdict is tested, the open-before-refuse order is not. A test could patch `builtins.open` in `test_symlink_out_of_root_is_refused`.
3. **An unreadable file is "file missing"** (01 section 4, "'Unreadable' folds into 'file missing'"). Only the non-UTF-8 case (H7) is tested; a permission-denied file is not.

### F4. Low. Some tests fix behaviour 01 does not ask for
- **Folder argument:** 01 never names it as a usage error; README task 2 adds that. It is tested at `tests/test_check_citations.py:194`. Fine.
- **Same output line:** `tests/test_check_citations.py:207-210` needs the reference text echoed verbatim, and `found at` on that same output line.
  - Failure path: a checker that prints `report.md:3 wrong line` and then `  found at notes.md:3` on the next line fails. 01 section 4 only says it "prints `found at path:line`".
- **Two cut shapes counted differently:** `tests/test_check_citations.py:121 "cc.find_refs("a.py:3:7"), ([], 0)"` counts 0 skipped, while `:113` counts a URL as 1. 01 section 2 lists both in the same "Cut" row.
- **Internal value fixed:** `tests/test_check_citations.py:95 "self.assertIsNone(r.start)"` fixes how a huge line number is stored. README task 3 asks only for the "no such line" verdict without `int()`.
- Each of these is a reasonable choice. It is now part of the spec, and the checker is held to it.

### Q1 (question, not a finding). Can task 4's done-check pass before task 5?
- `CliTests` (`:174`, docstring "(task 5)") and `SymlinkTests.test_report_run_in_the_copy` (`:166`) need the command line. Yet README task 4's done-check is the whole suite printing `OK`.
- Unless the command line is built in task 4, that done-check cannot pass. The plan sets this up, and the commit follows task 2. Is that intended?

### Notes (not findings)
- **Holds rows:** `GOLDEN`'s found column is `[]` there, while 01 lists the cited line (row 11 lists `notes.md:7`). It is never checked, because of the guard at `:145`.
- **Control characters:** the control-character test (`:217-223`) only checks ESC. A checker that never echoes the quote passes it trivially. It does not check that tab is kept.
- **Root in the summary:** `:183` checks only that the word "root" appears, not the root path.
- **Unneeded code:** none found. Every import is used. `FindTests` and `CliTests` are needed by the task 3 and task 5 done-checks; `python3 -m unittest tests.test_check_citations.FindTests` resolves the module and fails only on `check_citations`.

### Mutation (by reasoning; no files were written to run it)
- **Riskiest line:** `tests/test_check_citations.py:145 "if verdict != "holds":"`, with `:146 "self.assertEqual(result.found, found)"`.
- **The mutation:** change `:145` to `if verdict == "wrong line":`.
- **The wrong checker:** one that drops `found at` on "no such line" (rows 15-17; 01 section 4 says it "still prints `found at` if the words exist").
- **Result: not caught.** The only other found-at check is `:210`, which covers row 3, a "wrong line" row.
- **As written: caught,** by the row 15, 16 and 17 subtests.
- If `:146` were deleted, a wrong found-at on rows 10, 12 and 20 would also go uncaught. `:145-146` is the only guard, with no backup.

### Run
`timeout 120 python3 -m unittest discover -s tests 2>&1 | tail -3` printed:
```
Ran 1 test in 0.000s

FAILED (errors=1)
```
The only error is `ModuleNotFoundError: No module named 'check_citations'`, raised at `tests/test_check_citations.py:18`. `test ! -e check_citations.py && echo absent` printed `absent`. Task 2's done-check passes.

### Coverage
| Source | Status |
|---|---|
| README task 1 | Compared: files, bytes, H5-H7 rows and done-check all match |
| README task 2 | Compared: one 33-row table, exit codes 0/1/2 including folder, H3 temp copy and symlink, summary, done-check run. One gap (F1) |
| README tasks 3-5 | Compared against what the tests fix: task 3 shapes and H4 are covered; task 4's exact root check is not fully tested (F1); task 5's summary, ellipsis, colour and control characters are partly covered (F2, notes). Task 4's done-check timing raised as Q1 |
| 01 section 2 (shapes) | Compared: record wrapper, range, curly quote, backticks, fences, URLs, times, `path:line:col`, quote not scanned, absolute and `..` paths. Paths with spaces are not tested (01 cuts them) |
| 01 section 3 (match rule) | Compared: case, `**`, `_`, whitespace in the file, two-line quote, range, `...`. Not tested: first three places (F3), whitespace and backticks on the quote side |
| 01 section 4 (verdicts) | Compared: all 7 verdicts are used, `found at` on wrong line and no such line, exit 2 cases. Not tested: unreadable file (F3) |
| 01 section 5 (golden set) | Compared by script: fixture bytes, row texts, verdicts, found-at; counts rechecked. Rows 3, 10, 12, 15-17, 20, H4, H5 recomputed by hand |
| build-brief.md | Compared: fixtures and tests in one commit, no checker present, commit format, `unittest` only, no absolute paths in the committed files |
| Commit 3d59fa7 | Compared: export copy against `git show` (identical); the test file read in full; the suite run |
| Not compared | The rest of README (outside tasks 1-5), 01 section 1 and the Dog-food check, and 04-devils-advocate.md (cited by H5/H6 but out of scope). No stub checker was run, because no file writes were allowed, so the mutation is reasoned, not run |
