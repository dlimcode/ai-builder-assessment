## Unit-end review, area: the checker at 68f73d6

**Outcome:** the checker does what tasks 3 to 6 and 01 sections 2 to 5 ask, and its exit codes are right in every case you listed. I found one Medium and five Lows, plus one question. Nothing is Critical or High.

**What I ran:**
- The suite in the export: "Ran 40 tests … OK".
- Task 5's done-check: it ends with the 33-reference summary and `exit 1`. With the folder as argument it prints `exit 2`.
- Task 10's `git log` check prints `test(checker): add golden set before any code`.
- `planning/0*.md` has no commits on the branch.
- `check_citations.py`, its tests and `README.md` in the export are byte-identical to `git show 68f73d6:<file>`.

### F1. Medium. A code span split across two report lines is read inside out, so the dog-food run now shows 2 reds that nobody has explained
- **Where:**
  - `check_citations.py:85 "found, n = scan_line(line, number)"` scans one line at a time.
  - `check_citations.py:20 "(?P<code>(?P<ticks>`+).+?(?<!`)(?P=ticks)(?!`))"` then pairs the closing tick of the span from line 28 with the next opening tick.
- **Failure path:**
  - The input is `planning/demo-script.md:28-29 "point at row 3 (`wrong line, found at" … "notes.md:3`) and the `/etc/hosts:1` line"`.
  - The text between the ticks, "`) and the `", is skipped as code. Meanwhile the two examples are checked:
    - `planning/demo-script.md:29  notes.md:3  file missing`
    - `planning/demo-script.md:29  /etc/hosts:1  refused: outside root`
  - `timeout 60 python3 -B check_citations.py planning/*.md --root .` now prints "187 references: 89 holds, 0 line only, 21 red, 77 not checked".
- **What it breaks:**
  - The demo claim `planning/demo-script.md:9 "Measured: 89 references hold, 19 red, all real."` no longer matches the run.
  - The brief's done-when, `planning/build-brief.md:64 "every red it shows is explained in planning/decisions.md"`, now fails. The 01:39 entry in decisions.md explains 19 reds, not these two.
  - `README.md:39 "Anything in backticks, code fences or URLs is skipped"` is untrue for a code span that wraps onto the next line.
- **Smallest fix (my pick):**
  - Rewrap demo-script lines 28-29 so each code span sits on one line.
  - Add a decisions entry for the two reds.
  - Name "inline code across two lines" in README "What was cut".
  - The case against: it leaves the parser limit in place. Any hard-wrapped report can turn its examples into reds. Those reds are noisy but never a false green.

### F2. Low. The `isfile` guard that stops a hang on a FIFO has no test. This is the mutation result.
- **Where:** `check_citations.py:102 "if not os.path.isfile(target):"`
- **Mutation, in a temp copy:** `isfile` changed to `exists`.
  - All 29 checker tests still pass: H6 `data/` and H7 `bin.dat` still come out "file missing" through the `except` at :107.
  - Then a cited FIFO inside the root (`pipe.md:1 "x"`) blocks in `open()`. The run was killed by `timeout 10` (exit 124).
  - The original code prints "file missing" at once.
- **Fix:** one test that cites a FIFO made with `os.mkfifo` in a temp root, run under a subprocess timeout.
- **Second mutant, also not caught:** `check_citations.py:147` changed to `c != "\x1b"` passes all 29 tests. With it, BEL and backspace from a report reach stdout (checked with `od -c`). The only test of control characters checks ESC alone.

### F3. Low. Usage errors print the report name and `--root` unfiltered to stderr
- **Where:**
  - `check_citations.py:161 "parser.error("--root is not a folder: %s" % args.root)"`
  - `:165 "not a report file: %s"`
  - `:170 "cannot read %s: %s"`
  - None of these goes through `printable`.
- **Failure path:**
  - A clone holds a non-UTF-8 file in `planning/` whose name contains `ESC ]0;T BEL`.
  - `planning/*.md` expands to it, and the run exits 2.
  - Stderr carries the raw sequence (`cat -v`: `cannot read esc/c^[]0;T^G.md`), which sets the terminal title.
  - Likewise `--root $'x\e]0;PWNED\a'`.
- **Spec:** `planning/README.md:61 "characters below space except tab stripped"`. The summary's root is filtered; the error path is not.
- **Fix:** wrap the three `%s` values in `printable`.

### F4. Low. When printing fails, the run exits 1 ("red") or 120, not 0/1/2
- **Where:** `check_citations.py:188 "print(printable(...) + verdict)"`. Nothing catches an output error.
- **Failure path:**
  - `PYTHONIOENCODING=latin-1` with a report whose every reference holds but uses curly quotes: UnicodeEncodeError, traceback, exit 1.
  - `… | head -1` with `pipefail`: BrokenPipeError, exit 120.
- **What it contradicts:** `README.md:32 "Exit 1: at least one red."`
- **Fix:** `sys.stdout.reconfigure(errors="replace")`, and treat BrokenPipe as a quiet exit.

### F5. Low. Each reference re-reads and re-scans its whole cited file, even when the quote holds
- **Where:**
  - `check_citations.py:122 "lines = read_lines(root, ref.path)"`
  - `:126`: `places` scans every line before the holds test.
- **Measured** against one 20,000-line (770 KB) file:

  | References | Time |
  |---|---|
  | 100 | 2.5 s |
  | 400 | 9.3 s |
  | 1,600 | 36.6 s |

- **What I found and did not find:** the time grows with references times lines. I found no input that loops forever. A long report on a log file stalls for minutes.
- **Overlap with earlier reviews:** task-4-review-1 noted the re-read as surplus code, not as a cost.
- **Fix:** compute `places` only when the quote does not hold, and keep each file's lines per path.

### F6. Low. README says paths with spaces are skipped, but the last word is checked as the path
- **Where:**
  - `README.md:70 "paths with spaces, and URLs (skipped, not checked)"`
  - The lookbehind at `check_citations.py:18` starts the path after the space.
- **Failure path:**
  - With both `my notes.md` and `notes.md` in the root, `my notes.md:1 "under a minute"` is checked against `notes.md`. It printed "wrong line, found at notes.md:3".
  - If `notes.md` held the words on that line, it would be a false "holds" (exit 0).
- **Fix:** reword the README ("the part after the last space is taken as the path").

### Q1. Should a quote after punctuation still be checked?
- `notes.md:1, "Under a minute"`, `(notes.md:2) "anything at all"` and `notes.md:3: "x"` all come out "line only" (exit 0). The quote is never looked at (`check_citations.py:22 "[ \t]*([\"“])"`).
- This follows 01 ("right after the line number"). But it is the same silent green that a95a1be fixed for unclosed quotes, in shapes agents often write.
- Your call.

### Notes (not findings)
- **Exit codes, all measured:**

  | Case | Exit |
  |---|---|
  | A report that is not UTF-8 | 2 |
  | An unreadable report (mode 000) | 2 |
  | `--root` a file, missing, or `""` | 2 |
  | A FIFO as the report | 2 |
  | A symlink to a folder as the report | 2 |
  | The same report given twice | 0, every reference printed and counted twice |
  | An empty report ("0 references") | 0 |

- **The a95a1be fix holds:** an unclosed quote is checked to the end of the line. A straight open closed by a curly `”` runs to the end of the line and goes red, not green.
- **Outside root, all measured:**
  - A cited FIFO comes out "file missing".
  - A symlink to `/dev/zero` is refused.
  - A symlink loop comes out "file missing".
  - With `--root /`, `dev/zero` and `dev/stdin` come out "file missing".
  - `root/../a.md`, `./a.md` and `a.md/` hold inside the root.
  - I found no way to open or print a file outside `--root`. The swap-after-check race is already noted.
- **"found at" paths:** they are not passed through `printable`. They are built only from ASCII path characters and a `%d`, so no control character can reach them. They are safe as built today.
- **`printable` follows the spec exactly.** DEL, C1 controls (U+009B) and bidi overrides (U+202E) are not dropped.
- **Text shown can differ from text checked (by reading, not run):** `\x1c`-`\x1f` and `\x0b` count as spaces in `clean()` but are dropped when printing. So "under\x1fa minute" would show as "undera minute  holds".
- **The ellipsis note misses U+2026:** `"kettle … minute"` is "not in file" with no "not supported" note (`check_citations.py:184`, measured).
- **Code no task asked for:** `show_root`'s `~` substitution (`:150-152`). It keeps the home path out of pasted output, as the brief asks for committed files. Keep it.
- **Colour on a real terminal was not run:** the sandbox refused `openpty`. By reading, `:172 "colour = sys.stdout.isatty()"`. Off a terminal, no ESC was confirmed.
- **The main checkout shows ` M tests/test_scrub.py`:** that was not me. All my writes were in the temp folder.
- **Temp folder removal:** I ran `chmod -R u+rwx` before the prescribed `rm -rf` line, because of a mode-000 probe file. The folder is gone.

## Coverage
| Source | Status |
|---|---|
| planning/README.md, task 3 | Compared against `:17-88`, with probes. All of it is done. Gap: Q1. |
| planning/README.md, task 4 | Compared. Root check unchanged since review. Mutation F2 run on `:102`. |
| planning/README.md, task 5 | Compared, by running and probing every exit case. Gaps: F3 and F4. Colour on a terminal was read in the code, not run. |
| planning/README.md, task 6 | Compared, by running the dog-food command and reading each red against decisions.md. Gap: F1. `planning/0*.md` unchanged (git log). |
| planning/README.md, task 10 | Partly. The `git log` check passes. The suite was run in the export, not a fresh clone. The export matches the commit for the checker, its tests and README.md. Fixtures were not compared byte for byte. |
| 01, sections 2-5 | Compared with probes. Gaps: F1 (code spans), F6 (spaces), Q1, and the U+2026 note. The golden rows are verified by the passing suite and the run on `report.md`. |
| planning/build-brief.md | Compared: done-when items 1 and 2, the code rule, and no absolute paths in output (`~`). Gap: F1 (`:64`). |
| README.md | Every command run. Checker claims compared: F1 (`:39`), F4 (`:32`), F6 (`:70`); the rest are true. "How it was built" is not in my area. A task-7 review exists only after 68f73d6 (accb3c6). |
| check_citations.py | Read in full, run, probed, and two mutants run in temp copies. |
| tests/test_check_citations.py, fixtures, fixtures-evil | Read and run. The guard on `:102` and the non-ESC control characters are untested (F2). |
| Earlier reviews and the Lows in decisions.md | Read so as not to repeat them. F5 builds on a task-4 note but adds a measured cost. |
