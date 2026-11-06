# Unit report: check-citations (7 Nov 2026)

**Outcome:** `check_citations.py`, `scrub.py`, `planning/finish-sitting.sh`, README and demo script are built on
`build/check-citations`, 62 tests pass, and every Medium-or-worse finding is fixed and checked again. Not merged, not
pushed; the log export and scrub (task 13) and the merge (task 14) wait on Danish.

| Measure | Value |
|---|---|
| Time | 01:31 dry run, 01:33 first commit, 02:31 last check: about 1 hour of the 240 planned minutes |
| Tests | 62 (`python3 -m unittest discover -s tests`), all pass; a clean clone prints `OK` (task 10) |
| Dog-food | `planning/*.md`: 89 hold, 19 red, all explained (decisions 01:39); reviewers' notes: 26 red, real (task 12) |
| Reviews | 3 per-commit (tasks 2, 4, 7), 3 unit-end by area, 1 scoped re-review, 5 rechecks: `planning/reviews/` |
| Findings | Critical 0, High 4, Medium 21, Low 41 (plus questions) |
| Lows | 43 entries under `## Lows` in `planning/decisions.md`, for the sweep after the merge |

## Medium-or-worse findings and their fixes

| Review | Finding | Fix |
|---|---|---|
| task-2-review-1 | F1 Medium: the symlinked copy did not check counts | cb5bca6 (recheck: task-2-recheck-1) |
| task-4-review-1 | F1 Medium: an unclosed quote came out "line only" | a95a1be (recheck: task-4-recheck-1) |
| task-4-recheck-1 | F1 Medium: a curly quote closed at a straight mark | 0cb53ca (re-review: unit-rereview-fixes) |
| task-7-review-1 | F1 High: two reminders on one line | 2aa7047 (recheck: task-7-recheck-1) |
| task-7-review-1 | F2 High: wrapped or spaced list words missed | 2aa7047 |
| task-7-review-1 | F3 High: words left in branch history | 2aa7047 |
| task-7-review-1 | F6 Medium: a stale scrubbed log survived | 2aa7047 |
| task-7-review-1 | F4 Medium: path-shaped list entries never matched | 354f07e |
| task-7-review-1 | F5 Medium: an empty, `#` or BOM list passed anything | 354f07e |
| task-7-review-1 | F7 Medium: a quoted line ended a loaded text | 354f07e |
| task-7-recheck-1 | F1a, F2a, F7a Medium: cut too much, matched too much, a blockquote leaked | 2c4d52c (re-review) |
| unit-review-checker | F1 Medium: a wrapped code span made 2 unexplained reds | 65a489a (re-review) |
| unit-review-docs | F1 Medium (same as above); F2 Medium: README claimed undone work | 65a489a (re-review) |
| unit-review-scrub | F1 High: the saved session file was not read as records | ad698d1 (re-review) |
| unit-review-scrub | F2, F5, F6 Medium: indented blocks, slash entries, main's history | ad698d1 (re-review) |
| unit-review-scrub | F3, F4 Medium: stray tag, blockquote | already fixed by 2c4d52c (probes rerun on the head) |
| unit-review-scrub | F7 Medium: a hit's line pointed at an unwritten file | 9791fcf (re-review) |
| unit-rereview-fixes | F1, F2 Medium: a regression from 2c4d52c; one bad line dropped the records reading | 77e261a (recheck: unit-rereview-recheck-1, both fixed) |

Danish's own catches, fixed the same way: generic path patterns made `finish-sitting.sh` unable to pass (eaaef3a),
and a real folder name sat in a test and three reviews (eaaef3a, then the history rewrite and 21e2024).

## What is not verified
- The real `/export` format and the real saved session file: every scrub test uses made-up text. Danish's read of
  the real report's counts and of `logs/session.txt` is the check.
- Colour on a real terminal (the sandbox refused a terminal); by reading only.
- Whether the shell canary was stopped by the deny rule or the sandbox: auto mode stopped it first.

## Cards: only what Danish decides

**Card 1: Export and scrub the log (task 13)**
**What it is:** the session log goes public with the repo, so it is exported, scrubbed with your private list, and read before it is committed.
**Your options:** (a) do it now; undone by deleting `logs/session.txt` before a commit. (b) skip it and say so in README; undone by doing it later.
**My pick and the case against it:** (a), since the brief asks for the log. Against: the scrub has only seen made-up exports, so your full read is the real check.
**Your answer:** in this session type `/export logs/raw/session.txt`, then `/exit`; then in a terminal at the repo root `bash planning/finish-sitting.sh <private-list>`.

**Card 2: Delete the rewrite's backup refs**
**What it is:** `refs/original/refs/heads/build/check-citations` and the reflog still hold the three old commits with the old folder name; the branch's history check now finds 0 hits.
**Your options:** (a) delete them; this cannot be undone. (b) keep them; nothing local is pushed by default, but they stay on this disk.
**My pick and the case against it:** (a), after task 13's checks pass. Against: until then they are the only way back to the old branch.
**Your answer:** `refs: delete`

**Card 3: Delete the local review exports**
**What it is:** `.review/` (git-ignored, never committed) holds plain copies of old commits, three of them with the old folder name.
**Your options:** (a) delete `.review/`; cannot be undone, but every copy is rebuilt from git on demand. (b) keep it.
**My pick and the case against it:** (a). Against: nothing; the reviews cite repo paths, not these copies.
**Your answer:** `review folder: delete`

**Card 4: The commit author email**
**What it is:** every commit carries your personal webmail address as author, which goes public with the repo (docs review note).
**Your options:** (a) keep it. (b) switch to GitHub's noreply address: another history rewrite of every commit, main's too.
**My pick and the case against it:** (a), unless you mind it being public. Against: it is public for good once pushed.
**Your answer:** `email: keep` or `email: noreply`

**Card 5: Merge (task 14)**
**What it is:** merging `build/check-citations` into main, after cards 1 and 2.
**Your options:** (a) merge; undone by resetting main before any push. (b) hold.
**My pick and the case against it:** (a) once the log is in. Against: 43 Lows remain, a few of them ways a check can pass wrongly (e.g. quotes match as substrings).
**Your answer:** write `yes` under `question:` in `planning/build-brief.md`, then, at the repo root, `bash planning/start-sitting.sh`.
