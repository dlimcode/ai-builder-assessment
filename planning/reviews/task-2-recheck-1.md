## Recheck of cb5bca6: F1 and F2 are fixed on this Mac. The new check only works because this machine's temp folder sits behind a symlink.

**Answers to the three questions**

| # | Question | Result |
|---|---|---|
| 1 | Does the suite fail if `root = os.path.realpath(root)` (check_citations.py:97) becomes `pass`? | **Yes.** 27 ran, 2 failures and 2 errors. `test_report_run_in_the_copy` is among the reds. The other three reds are the CliTests `test_golden_report_summary_and_exit` and `test_ellipsis_is_named` (errors) and `test_red_line_says_where_the_words_are` (failure). Those three are not caused by the symlink. They pass a relative `--root tests/fixtures`, so `os.path.commonpath` raises `ValueError: Can't mix absolute and relative paths`. Running from the resolved `/private/tmp/...` path gives the same 4 reds. |
| 2 | Did the fix break what it touched? | **No.** The unmodified export runs 27 tests, OK. `summary_counts` reads the real line `33 references: 10 holds, 1 line only, 20 red, 2 not checked (root: …)` as `(33, 10, 1, 20, 2)`. "11 line only", "120 red", "12 not checked" and "133 references" all give different tuples, so all fail as they should. |
| 3 | Does the mutation pass the pre-fix test file (`git show 3d59fa7:tests/…`, which is identical to 1e0a07c's)? | **Not as asked.** With `pass`, the pre-fix suite is already red: the same 3 CliTests fail because of the relative-root crash. `test_report_run_in_the_copy` is green there. A cleaner mutation for F1's bug, which turns the root into an absolute path without resolving the symlink, is `root = os.path.abspath(root)`. With it, the pre-fix suite runs 27, OK. The post-fix suite has exactly one red: `test_report_run_in_the_copy`, with `Tuples differ: (33, 0, 0, 31, 2) != (33, 10, 1, 20, 2)`. So the new assertion is what catches F1's bug. |

One correction to the review: F1 says dropping `realpath(root)` "passes every test". For the checker as built, plain removal is already caught by the relative-root crash. Only the `abspath` form slipped through, and that is the gap this fix closes.

### F1. Low. The new assertion only catches the bug where the temp folder is a symlink
- `tests/test_check_citations.py:159 "self.tmp = tempfile.mkdtemp(prefix="cc-golden-")"`
- `tests/test_check_citations.py:178 "# The copy's root may sit behind a symlink (/tmp)"`
- **Failure path:**
  1. Run on a machine whose temp folder is a real folder, such as most Linux CI `/tmp`, or here with `TMPDIR` set to a resolved path.
  2. The root `--root` gets has no symlink in it.
  3. The `abspath` mutation then passes all 27 tests. I ran this: TMPDIR set to `/private/tmp/.../t`, post-fix tests, result OK.
- **Fix:** make the test build its own symlinked root rather than rely on the machine. Point a link at `self.root` and pass `--root` through that link.

### F2. Low. A missing summary part errors without saying what the line was
- `tests/test_check_citations.py:63 "int(m.group(1)) for m in (re.search(...`
- **Failure path:** if a part such as "line only" is missing from the line, `re.search` returns None. The test then raises `AttributeError: 'NoneType' object has no attribute 'group'` (I ran this on a string). It is still red, but the `out.stdout` / `last` message at :179 and :189 never prints.
- This is cosmetic: the test still goes red.

**Coverage**

| Item | Status |
|---|---|
| Review F1 section (planning/reviews/task-2-review-1.md:28-39) | compared |
| Review F2 section (:41-47) | compared |
| Other sections (F3, F4, Q1, Notes) | not compared (outside the brief) |
| Diff, `git show cb5bca6 -- tests/test_check_citations.py` | compared, all 3 hunks. The diff of planning/reviews/task-2-review-1.md was not compared (only F1 and F2 were in scope). |
| Run 1 (`pass` mutation, post-fix tests, under /tmp; repeated from /private/tmp) | compared |
| Run 2 (unmodified suite, real summary line, F2 strings) | compared |
| Run 3 (`pass` on pre-fix tests, plus an added `abspath` run on pre- and post-fix tests) | compared |
| Second `realpath(root)` at check_citations.py:150 (`show_root`, display only) | not compared (not part of F1) |

Every temp folder was made and removed by the given rules. Nothing was written in the repo; I used `python3 -B` in the export so no cache files were left. `git status` shows `M planning/decisions.md`, which I did not touch: it changed elsewhere during this run.
