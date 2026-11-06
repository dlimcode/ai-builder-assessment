(Edited on Danish's instruction, 7 Nov: a real folder name in the test's example was replaced by the invented "Zephyr"; "Old Shoebox" is a listed generic path, so that test case could not use it.)

Review of 6be8f92: the code runs and all 63 tests pass. But a real private word can now get through the export gate in two ways. The scrub then exits 0 and writes the log, and the hit shows only in the report's "generic pattern hits" section.

### F1. High. A line break after `~/Documents/` (or before `/folder`) lets a folder under `~/Documents` pass
- **Where:** `scrub.py:284 "[spaced("~/Documents") + r"/?(?![/\w.-])"]"`.
- **Why it fails:** the lookahead checks only the very next character. A line break isn't in `[/\w.-]`, so the bare-`~/Documents` phrase matches and `scrub.py:290` turns it into `<generic>\n`. The folder name on the next line is cut off from it. `list_hits` on the masked text (`scrub.py:340`) finds nothing.
- **Failure path:** list entry `<home>/Documents/Clients` (read as `~/Documents/Clients` after pass 2), log `see ~/Documents/\nClients/notes`. Result: exit 0, `logs/session.txt` written, "private list: 0 hits". The unmasked text did hit, at (line 1, entry 1); I checked in-process.
- **Same result (exit 0, written) for:**
  - the raw home path wrapped the same way (`<home>/Documents/\nClients`);
  - `~/Documents\n/Clients`;
  - entry `<home>/Documents` with `~/Documents/\n<folder>`;
  - entry `Documents/Clients` with `~/Documents/\nClients`.
- **Controls:** the same inputs without the line break exit 1, and so does `Documents/\nClients` with no `~/` in front.
- **What this breaks:** the stated rule "any folder under `~/Documents` still fails" (`planning/decisions.md:246 "~/Documents/<folder>` still fails"`). It also defeats the wrapping that `list_hits` is built to catch (`scrub.py:219 "so a word split by terminal wrapping"`).
- **Test gap:** the test only tries the unwrapped form (`tests/test_scrub.py:304 "see ~/Documents/Zephyr\n"`).
- **Possible fix:** make the lookahead skip whitespace, e.g. `(?!\s*[/\w.-])`. The cost: a bare `~/Documents` at the end of a line followed by a word would then fail. That is the safe side to err on.

### F2. Medium. The phrases have no word boundary, so an entry that runs past a phrase passes
- **Where:** `scrub.py:283 ""/Users/alex", "-Users-alex", "/Users/someone", "~/Documents/Old Shoebox", "@example.com""` and `"claude-501"`. Only the bare `~/Documents` has an end check; no phrase has a start check.
- **Why it fails:** the phrase masks the front of a longer word. The rest of the word is left beside `<generic>`, so a hit that is not wholly inside the phrase is still hidden.
- **Failure path:** entry `Alexandra`, log `cd /Users/alexandra/work`. The masked text is `cd <generic>andra/work`. Result: exit 0, written. The control `Alexandra wrote` exits 1.
- **Same result (exit 0) for:**
  - `-Users-alexandra-work`;
  - entry `Old Shoebox Holdings` in `~/Documents/Old Shoebox Holdings/a`;
  - `example.community` in `@example.community`;
  - `alex acme` in `/Users/alex acme`;
  - `someonelse` in `/Users/someonelse/x`;
  - `claude-5017`;
  - `Tan/Users` in `Tan/Users/alex` (crossing the phrase's start).
- **How likely:** it needs a private word that starts with, or runs on from, one of these made-up phrases. `alex` is a common start of first names.
- **Possible fix:** add `(?<![\w-])` before each phrase and `(?![\w-])` after it, whitespace-tolerant as in F1.

### Notes and questions
- **Question:** should `~/Documents/ Clients` (a space, same line) pass? It now exits 0 (entry `<home>/Documents`); before this commit it failed. It could be two arguments or a wrapped path with an indent.
- **The `<generic>` placeholder:** an entry `generic` now fails on `/Users/alex/x`, which has no such word. That fails safe and is unlikely. It also means `scrub.py:342` can't report that hit as generic, because it is not in `all_hits`.
- **What I found safe:**
  - Case: `/USERS/ALEX/x` with entry `alex` passes as generic, as meant.
  - Wrapping inside a phrase followed by a listed word (`/Users/al\nex\nAcme Widgets`) still fails, as meant.
  - The `\s*` between characters only takes up whitespace, so a phrase can't swallow a word. I worked this out from the pattern and did not run it.
  - The space in `Old Shoebox` is an escaped literal space, so `Old\nShoebox` is not masked and fails safe. Also worked out, not run.
  - The email-pattern phrase matches only its own literal text, and pass 3 does not change that text.
  - Overlap with the path pass: masking runs after pass 2, so raw home paths behave like `~` (case A2 above).
- **Scope:** the commit does only what was meant. `spaced`, `GENERIC_TEXT`, `mask_generic`, four lines in `main`, the report header and the two 02:59 entries. Nothing extra. `--check-only` (`scrub.py:317-327`) is unchanged, as intended.
- **The decision entry overstates:** "the text around it is still checked" (`planning/decisions.md:246`) is not true for F1 and F2.
- **Mitigation:** each masked hit is listed under "generic pattern hits" (`scrub.py:342`), and `planning/finish-sitting.sh:44` says to read both reports in full. That relies on a person reading; it does not stop the log being written.

### Mutation
- **Line:** `scrub.py:284`. The lookahead was removed (`r"/?(?![/\w.-])"` became `r"/?"`) in a full copy of the tree in a temp folder.
- **Result:** caught. 63 tests ran, 1 failed: `test_generic_text_in_the_export_is_reported_not_failed`, subTest `see ~/Documents/Zephyr\n`.
- **Not caught by any test:** the F1 and F2 inputs, which pass with the code as committed.

### Runs
- `timeout 180 python3 -m unittest discover -s tests` in the exported tree: 63 tests, OK.
- A probe script ran `scrub.py` end to end on 21 made-up list/log pairs in a temp folder (exit code, whether the log was written, last report line). An in-process check compared masked and unmasked hits for three F1/F2 cases. The temp folders were removed.

### Coverage
| Source | Status |
|---|---|
| the diff | Compared: read in full. Every changed line was checked against the stated intent; F1 and F2 come from it. |
| scrub.py | Compared: read in full, ran, probed and mutated. F1 at line 284, F2 at line 283. |
| tests/test_scrub.py | Compared: read the new test (lines 287-306), the generic test before it and the fixtures at the top. Ran the whole suite. Not compared: the remaining older tests, read only through the run. |
| planning/finish-sitting.sh | Compared: read in full. It calls `scrub.py` as `<export> <out> <list> <report>` (line 20), so exit 0 there means `logs/session.txt` is written. Not run: it needs `logs/raw/session.txt` and a real list. |
| planning/decisions.md (02:59 entries) | Compared: read both. The claim that the text around a phrase is still checked is contradicted by F1 and F2. The claim about a real-export run with a stand-in list was not checked: that export and list are not in the tree. |
