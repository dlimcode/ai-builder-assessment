# Review of a7bbd9b (task 4) and 98cb10d (task 3)

**Outcome:** the root check matches the task text line for line, and the passing suites pass. I found one Medium (an unclosed quote turns into a silent green) and four Lows. Nothing is Critical or High.

- **Export:** the copy is byte-identical to the commit. I compared both files with `git show a7bbd9b:<file> | cmp -`.
- **Suites:**
  - FindTests and GoldenTests: "Ran 16 tests ... OK".
  - `SymlinkTests.test_symlink_out_of_root_is_refused`: OK.
  - Full suite: 27 tests, 7 failures and 1 error. They are all in CliTests or `SymlinkTests.test_report_run_in_the_copy`, which is expected.
- **Root check, against planning/README.md task 4:**
  - `check_citations.py:95 "root = os.path.realpath(root)"` and `:96 "target = os.path.realpath(os.path.join(root, path))"` match the task text.
  - `:97 "if os.path.commonpath([root, target]) != root:"` refuses, `:99` gives "file missing" unless `isfile`, `:102` opens with `encoding="utf-8"`, and `:104` turns a decode error into "file missing". No `strict=` is used.
  - Nothing is opened before line 97. `realpath` only runs lstat and readlink.
- **Root probes, all correct:**
  - A symlinked root (`/tmp/claude-501` → `/private/tmp/...`): a missing file inside it is "file missing", not refused.
  - A sibling with the root's name as a prefix (`../claude-501x/a.md`) is refused.
  - A root with a trailing slash works. `data/../../fixtures/notes.md` is allowed.
  - A 6000-character path, `data/`, `bin.dat` and a root that does not exist all give "file missing".
- **Line endings, probed with in-memory files:** CRLF, a lone CR, no trailing newline, a trailing blank line, a byte-order mark, Latin-1 and U+2028 all behave correctly.
- **Matching against 01 section 3:**
  - Cleaning is right (`:90`): it strips backticks and `**`, collapses whitespace and keeps case.
  - A two-line quote is right (`:111-115`), and so is a range (`:132`).
  - The whole-file search keeps the first three places (`:123`). All 7 verdicts follow the order in section 4.

### F1. Medium. An unclosed or mismatched quote becomes "line only" (exit 0), and its words are then scanned as references
- **Where:** `check_citations.py:61 "close = text.find(QUOTE_CLOSE[q.group(1)], q.end())"` and `:62 "if close != -1:"`. With no closing mark, `quote` stays None and `pos` does not move past the opening mark.
- **Failure path:**
  - `notes.md:3 "Under a minute` (closing mark forgotten) gives `line only`, which exits 0. The same reference with the quote closed gives `not in file` (red).
  - The same happens for `notes.md:3 “under a minute"` (curly open, straight close).
  - It also happens for a quote that a hard-wrapped report line splits onto the next line, which is common in this repo's 120-column markdown.
  - Because `pos` is not advanced, `a.md:1 "see notes.md:2` yields two references. That breaks 01:37 "Words inside a quote are not scanned for references".
- **Spec:** 01:68 says "line only ... no quote given". Here a quote was given but never closed. 01:32 ("same line") does not say what an unclosed quote should be.
- **Smallest fix to consider:** give an opened but unclosed quote its own red verdict, or count it as "not checked". Either way it should not be green.
- **Smaller case of the same kind:** an empty quote, `notes.md:3 ""` or `"**"`, is also `line only`.

### F2. Low. The match is on any substring, not whole words, so a negated word can pass
- **Where:** `check_citations.py:115 "joined.find(words)"` and `:132 "words in \" \".join(...)"`.
- **Failure path:** the file line is "This script is unsafe to run." and the reference is `notes.md:1 "safe to run"`. The result is `holds`, measured with an in-memory file.
- **Also:** `notes.md:3 "inute"` holds.
- **Spec:** 01:49 says "exact words after light cleaning" but never sets word boundaries. This is a reading of the spec for Danish to settle, not a clear departure from it.

### F3. Low. Scanning time grows with the square of a long run of letters or digits (polynomial, not catastrophic)
- **Where:** the URL branch of `check_citations.py:18 "(?P<url>[A-Za-z][A-Za-z0-9+.-]*://\S*)"`. From every letter it runs to the end of the run, looking for `://`.
- **Measured:**

  | Input | Time |
  |---|---|
  | 5,000 letters | 0.034 s |
  | 20,000 letters | 0.55 s |
  | 40,000 letters | 2.2 s |
  | The URL branch alone, 40,000 letters | 2.15 s |

  At that rate 100,000 letters would take about 13 s. That is an estimate, not measured.
- **Shapes that stayed fast:** an unclosed backtick before plain text (same cost as letters, because of the URL branch, not the backtick), alternating backticks, and path characters with no colon.
- **Failure path:** a report with one long base64 or minified line stalls for seconds. Nothing grows exponentially.

### F4. Low. Words over three or more lines, cited at the wrong place, come out "not in file" although they are in the file
- **Where:** `check_citations.py:123` builds `places` only from `starts_at`, which looks at one line or two. `:135` then says "not in file".
- **Failure path:** `notes.md:5 "door is the side entrance. Deliveries arrive before eight and are signed"`. The words run over lines 5-7, and the result is `not in file` with no places. The same happens when cited as `3-4`.
- **Spec:** 01:70 says "not in file ... words nowhere in the file". The right verdict is "wrong line", which here cannot point anywhere.

### F5. Low. Two risky lines have no test guarding them
I made each change in memory and ran it against FindTests, GoldenTests and `test_symlink_out_of_root_is_refused`.

| Change | Result |
|---|---|
| `:97` commonpath compared with `target.startswith(root)` | **Caught**, 2 failing (H5, the prefix sibling) |
| `:97` compared with `os.path.dirname(root)` | Caught, 31 failing |
| `:96` target uses `normpath` instead of `realpath` | Caught (the symlink test) |
| `:115` `< len(here)` loosened | Caught, 5 failing |
| `:95` `os.path.abspath(root)` instead of `realpath` | **Survived** |
| `:123` `[:3]` changed to `[:2]` | **Survived** (no golden row has more than 2 places) |

- **Why the abspath change survives:** on macOS the test's temp root sits under `/var` → `/private/var`, so every reference is refused. That includes the one the test expects refused, so the test still passes.
- **What it would break:** it only refuses too much; it does not open a way out of the root. A real `--root` reached through a symlink would turn every reference red.
- **Missing tests:** a reference that holds under a symlinked root, and a row with 4 or more places.
- **Not run:** removing the check entirely. It would open `/etc/hosts`, outside the read fence. It would be caught, because H2 expects "refused".

## Notes (not findings)
- **Unicode digits:** `\d` matches them, so `notes.md:٣` resolves to line 3. Harmless.
- **Trailing slash:** `notes.md/:3` holds, because `realpath` drops the slash. The file is still inside the root.
- **Addresses:** `127.0.0.1:8080` and `example.com:443` become references and go "file missing". That follows the path definition in 01 section 2 literally.
- **Backticks:** in an unmatched double backtick such as ``` ``notes.md:1 "x" ` ```, the regex backtracks to a single tick and skips the reference. It is still counted "not checked", so it shows.
- **Fences and code spans:**
  - A closing fence that carries an info string still closes the block.
  - Inline code that runs over two lines is not handled.
  - Inside a fence the skip count is per line; inline it is per span.
- **Time between check and open:** a symlink could be swapped after the check and before the open. This is outside the threat model.
- **Code the task did not need:**
  - `Ref.raw` (`:11`) is unused until task 5.
  - The module docstring describes a command line that does not exist yet.
  - `check` re-reads the file for every reference, and it computes `places` even when the quote holds.

  All of this is small. None of it is worth cutting now.
- **Tests that pass for the wrong reason:** two CliTests pass now only because the module has no main. They are `test_all_green_exits_0` and `test_no_colour_and_no_control_characters_off_a_terminal`. They test nothing until task 5.
- **Task 3 (98cb10d):**
  - **Done as written:** path shape, the record wrapper (left as plain text around the match), a straight or curly quote right after the line number with spaces or tabs between, skipping backticks, fences and URLs, rejecting path:line:col (`:36`), and digit runs over 9 kept out of `int()` (`:27`). A 12-digit `000000000003` is "no such line", as the rule says.
  - **Broken:** an unclosed quote (see F1).

## Coverage
| Source | Status |
|---|---|
| planning/README.md, Task 3 and Task 4 | Compared line by line against `:15-85` and `:93-108`. The root check matches exactly. |
| planning/01-prior-art-and-formats.md, section 2 | Compared, with probes. Gaps: F1, the address shapes in the notes. |
| planning/01, section 3 | Compared, with probes. Gaps: F2, F4. The "`...` is not supported" message is left to task 5 (CliTests). |
| planning/01, section 4 | Compared: all 7 verdicts and their order. Gap: F4. |
| planning/01, section 5 | Compared through GoldenTests, which pass, and `GOLDEN` against the table. All rows match. H5-H7 are inferred from the tests only. |
| planning/build-brief.md | Compared against the code rule. No input or security check is cut. Gaps: F5 (missing tests) and the small extra code in the notes. |
| check_citations.py (export) | Read in full, run, and probed: edge cases, timing, 6 mutants. |
| tests/test_check_citations.py (export) | Read in full and run. Failures are the expected set only. |
| `git show a7bbd9b` / `git show 98cb10d` | The diff stats were read and the export was confirmed identical to the commit. The changes themselves were reviewed in the exported file, which holds both commits' code. |
| README task 1 rows H5-H7, the fixture contents, and a run on `planning/*.md` | Not compared: outside my read list. GoldenTests checks report.md against the table. A run on `planning/*.md` would show whether F1 already happens in this repo's own notes. |
