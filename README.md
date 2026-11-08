# check_citations

Checks that the words an AI report quotes are really on the file line it cites.

## What it is

An agent writes `notes.md:3 "under a minute"` in a report. `check_citations.py` opens `notes.md`, looks at line 3,
and says green if those words are there, or red with where the words really are. One Python 3.9 file, standard
library only, no model call, no API key.

```
tests/fixtures/report.md:1  notes.md:3 "under a minute"  holds
tests/fixtures/report.md:3  notes.md:4 "under a minute"  wrong line, found at notes.md:3
tests/fixtures/report.md:15  notes.md:40 "under a minute"  no such line, found at notes.md:3
tests/fixtures/report.md:20  data/plan.txt:2 "water the plants"  wrong line, found at data/plan.txt:1, data/plan.txt:3
33 references: 10 holds, 1 line only, 20 red, 2 not checked (root: ~/.../tests/fixtures)
```

## How to run it

Nothing to install; Python 3.9 or later.

```
python3 check_citations.py REPORT.md [REPORT.md ...] [--root DIR]
python3 check_citations.py planning/*.md --root .
python3 -m unittest discover -s tests
```

- Arguments are files; the shell expands `planning/*.md`. A folder argument is a usage error.
- `--root` (default: the current folder) is where cited paths start. The summary line names it, because a wrong
  root turns every reference into "file missing".
- Exit 0: nothing red. Exit 1: at least one red. Exit 2: a usage error (no such report, a folder, a bad flag).
- Colour only on a terminal; control characters from a report are dropped before printing.

## How it decides

A reference is `path:line` or `path:first-last`, optionally inside `[record ...]`, optionally followed on the same
line by a quote in straight or curly marks. A path is letters, digits and `_ . / -` holding a `.` or `/`, so `12:30`
is not one. Anything in backticks (on one line), code fences or URLs is skipped and counted "not checked".

| Verdict | Colour | When |
|---|---|---|
| holds | green | the words are on the cited line or range |
| line only | neutral | no quote; the line exists |
| wrong line | red | the words are elsewhere in the file (up to three places listed) |
| not in file | red | the words are nowhere in the file |
| no such line | red | line 0, past the end, a reversed range, or a number of 10+ digits |
| file missing | red | no such file, a folder, or not UTF-8 text |
| refused: outside root | red | after resolving `..` and symlinks, the path is outside the root; nothing is opened |

The match rule, in four lines:
- Exact words, case kept, after light cleaning: whitespace runs become one space; backticks and `**` are dropped.
- A quote may start on the cited line and run into the next.
- A range holds if the words are anywhere in its lines joined.
- A quote with no closing mark runs to the end of the line and is checked like any other.

## Trade-offs

- **Exact match, case kept.** `"Under a minute"` is red against "under a minute". "Exact" stays exact; the cost is
  noise on harmless changes. Matching is on characters, not whole words: `"safe to run"` holds on "unsafe to run".
- **No near-line tolerance.** One line off is red, with where the words are: an off-by-one line is the mistake the
  tool exists to catch.
- **One root.** Paths resolve against `--root`, not the report's folder and not the nearest `.git`, so repo-relative
  references work on any clone or zip. Run from the wrong folder and everything is "file missing"; the summary says
  which root it used.
- **Whole files are read into memory.** Reports cite source files, not multi-gigabyte data; accepted for v1.

## What was cut

- URLs (skipped, counted "not checked"); `path:line:col` and `#L12` anchors (dropped, not counted).
- Paths with spaces: the part after the last space is taken as the path, so `my notes.md:1` checks `notes.md`.
- Inline code that wraps onto the next line: the backticks pair up wrongly, and the examples in it are checked.
- `...` inside a quote: taken literally, so a shortened quote is red, and the line says "`...` is not supported".
- Fuzzy or case-blind matching, a near-line tolerance, an "also at" note when a green quote repeats.
- Folder arguments (walking a tree), JSON output, a package or CI, any model call at run time.

## Weakest part and what next

It cannot tell a file that changed after the report was written from a citation that was wrong when written: both
come out "wrong line". Next: `--at <commit>`, reading each cited file as it was at that commit (`git show`), so a red
means the agent was wrong, not that the file moved on.

`planning/finish-sitting.sh` still exits 1 on this repo: its private-list hits in the log (the harness temp folder
name) and in the files and history (made-up test paths, the scrub's own email pattern, the temp folder) were read
and accepted by hand, not by the script. A run that exits 1 still needs a person to read both reports.

Smaller known gaps are listed under `## Lows` in `planning/decisions.md` (for example, words spread over three or
more lines and cited at the wrong place come out "not in file").

## How it was built

- **Claude Code in the terminal**, in one desk sitting on 7 Nov 2026. A planning team of subagents wrote
  `planning/00-04*.md`; `planning/README.md` is the task list the sitting followed.
- **Tests before code:** the 33-row golden set and its fixtures were committed before `check_citations.py` existed
  (`git log --reverse --oneline`).
- **Review:** a fresh reviewer agent read the commits for tasks 2, 4 and 7, a fresh agent rechecked each fix of a
  Medium-or-worse finding, and three more read the branch at the end. Their replies are in `planning/reviews/`;
  the fixes are `fix` commits whose `Fixes:` trailers name the finding (one commit may fix several).
- **`planning/decisions.md`:** each moment the agent helped, failed or was corrected, written during the sitting;
  three entry times were guessed and then corrected (its own entry says so). Smaller known gaps are its `## Lows`.
- **Logs:** `logs/session.txt` is the build session's `/export`, scrubbed by `scrub.py` (start-up blocks, this
  machine's paths, emails, tokens; then a private word list kept outside the repo) and read in full by a person.
  It is not every session: the planning team's work before 01:05 on 7 Nov, the short fix session after the
  export, and the 8 Nov doc fixes are not in it. Their output is in `planning/` and `git log`.
- **Time, 7 Nov:** planning about 30 minutes; the build 01:33-02:35; the log, its scrub and the fixes to 03:32.
  Making the log safe to publish took longer than it should have, about as long as the build. `scrub.py` is a
  side tool for that job, not part of the checker.
- **Commit trailers:** each commit carries a `Claude-Session:` id (a session id, nothing private); they stay unless
  stripped before publishing.
