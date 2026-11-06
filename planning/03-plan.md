# 03 The build sitting's plan (7 Nov 2026)

**Outcome: 14 tasks, 220 minutes plus a 20-minute buffer (240 at most); the golden set and its tests are committed
before any checker code; the tool is `check_citations.py`; the demo's red moment is both a real run on `planning/`
and a staged "file edited after the report" run that turns every reference into that file red.**

Tags as in 01 and 02: `[Danish]`, `[record path:line "words"]`, `[measured, how]`, `[source, date read]`, `[assumed]`.
Every minute figure is `[assumed]`. Picks are this role's recommendation, not a decision. "The sitting" is the one
3-4 hour desk session in which Claude Code builds the tool [Danish] ("maybe i can take 3-4 hours with this? just one
desk sitting to complete."). "/build" is Danish's own build recipe, a Claude Code skill started by the first prompt.

## 1. What is built
- **Name and command:** `python3 check_citations.py <file or folder> [--root DIR]`. A folder means every `.md` under
  it, sorted. Paths in references resolve against `--root`, default the current folder [record planning/01-prior-art-and-formats.md:40 "Paths resolve against one root"].
- **Match rule and verdicts:** exactly 01 sections 2-4 [record planning/01-prior-art-and-formats.md:49 "exact words after light cleaning"]; seven verdicts.
- **Exit codes:** 0 all hold (line only and not checked do not fail), 1 any red, 2 usage error
  [record planning/01-prior-art-and-formats.md:75 "Exit 2 for usage errors"]; a bad flag gets argparse's own exit 2 [assumed].
- **Output** (one line per reference, verdict in words, colour only when printing to a terminal, so the words carry it):
```
tests/fixtures/report.md:1   HOLDS          notes.md:3 "under a minute"
tests/fixtures/report.md:3   WRONG LINE     notes.md:4 "under a minute"   found at notes.md:3
tests/fixtures/report.md:13  LINE ONLY      notes.md:3
tests/fixtures/report.md:29  REFUSED        ../outside.md:1 "x"   outside root
root: tests/fixtures | 30 references: 10 holds, 1 line only, 17 red, 2 not checked
```
- **Layout:** `check_citations.py` (one module, about 150 lines [assumed]), `tests/test_check_citations.py`,
  `tests/fixtures/` (01's `notes.md`, `data/plan.txt`, `empty.md`, `report.md`); then `scrub.py` with `tests/test_scrub.py`
  (02 section 3); `README.md`; `planning/decisions.md`, `planning/demo-script.md`; `logs/` (scrubbed export only).
- **Python 3.9.6, standard library only:** no `match`, no `X | None` outside annotations; tests run with
  `python3 -m unittest discover -s tests` from the repo root (`-m` puts the current folder on the import path) [assumed].

## 2. The sitting, in order (each task one commit or more, `type(scope): subject`)

| # | Task | Min | Ends at | Done-check: command, then what it prints |
|---|---|---|---|---|
| 0 | Start: `bash planning/start-sitting.sh`; on branch `build/check-citations`; add `logs/raw/` to `.gitignore`; create `planning/decisions.md` from section 6 | 5 | 5 | `git branch --show-current` prints `build/check-citations`; `grep -c raw .gitignore` prints `1` |
| 1 | Fixtures: 01's files byte for byte; `report.md` = rows 1-26 then H1-H4, one per line | 15 | 20 | `wc -l < tests/fixtures/notes.md` prints `9`; `wc -l < tests/fixtures/report.md` prints `30`; `wc -c < tests/fixtures/empty.md` prints `0` |
| 2 | Tests, red: the 30 rows as a table in the test file; CLI exit 0/1/2; H3's symlink made in a temp copy of the fixtures; commit `test(checker): add golden set before any code` | 25 | 45 | `python3 -m unittest discover -s tests 2>&1 \| tail -1` prints `FAILED (errors=...)`; `ls check_citations.py` prints `No such file` |
| 3 | Find references: path shape, `[record ...]` wrapper, first straight or curly quote, skip backticks, fences, URLs | 25 | 70 | `python3 -m unittest tests.test_check_citations.FindTests` prints `OK` |
| 4 | Match and verdicts: cleaning, two-line quote, range, search the file (first three places), refuse outside root before opening | 30 | 100 | `python3 -m unittest discover -s tests 2>&1 \| tail -1` prints `OK` |
| 5 | Command line: folder input, summary line with the root, exit codes, colour on a terminal only | 15 | 115 | `python3 check_citations.py tests/fixtures/report.md --root tests/fixtures; echo $?` prints the summary above, then `1` |
| 6 | Dog-food: `python3 check_citations.py planning/ --root .`; each red is a checker bug (fix with a test) or a real miscite (record it in decisions, never edit an old planning file); rehearse the staged red (section 3) | 10 | 125 | `git status --short planning/` prints only ` M planning/decisions.md` |
| 7 | Scrub step: `scrub.py` and its one test (section 7) | 20 | 145 | `python3 -m unittest tests.test_scrub` prints `OK` |
| 8 | `README.md` from section 5 | 15 | 160 | `grep -c '^## ' README.md` prints `7` |
| 9 | `planning/demo-script.md` from section 4 | 10 | 170 | `grep -c '^## ' planning/demo-script.md` prints `6` |
| 10 | Clean clone: clone into a temp folder, run the tests there | 5 | 175 | last line `OK` |
| 11 | /build's unit end: three fresh reviewers on the branch, fixes, `planning/unit-report.md` | 20 | 195 | `ls planning/unit-report.md` prints the path |
| 12 | Decisions log read through: every entry has a time and a commit or "none" | 5 | 200 | `grep -c '^## ' planning/decisions.md` prints 6 or more [assumed] |
| 13 | Logs: `/export logs/raw/session.txt`, quit; Danish runs the scrub in his own terminal, reads the report, commits `logs/session.txt` | 15 | 215 | `git ls-files logs` prints only `logs/session.txt`; the report's last line `private list: 0 hits` |
| 14 | Merge: Danish writes `yes` under the brief's `question:`; a thread started from the brief merges | 5 | 220 | `git log main --oneline \| head -1` shows the merge |

- README, decisions, scrub, export and demo script: tasks 7, 8, 9, 12, 13 = 65 minutes. Checker build (tasks 1-6): 120.
- **Git order shows tests first:** `git log --reverse --oneline` lists the test commit (task 2) before any commit
  touching `check_citations.py`; the done-check of task 2 proves the file did not exist.
- **Cut line:** if task 4 is not `OK` by minute 120, cut in this order and say so in the README: folder input (one
  file only), colour, then rows 9-10 and 23 (two-line quote, curly quotes) marked `expectedFailure` with a reason.
  Never cut H1-H4 (outside root, absolute path, symlink, huge number) or the exit codes.
- **/build's own steps, set by the brief:** a fresh reviewer agent checks each commit in the background (replies saved
  under `planning/reviews/`); the plan it reads is `planning/README.md`, whose tasks must be headed `### Task N:`
  [measured, read of the /build skill file, 7 Nov]. Its worktree step would make a folder beside the repo, outside the
  session's read fence, so the start script switches the repo itself to the branch first [measured, same read].

## 3. The demo's red moment: both
1. **Real:** `python3 check_citations.py planning/ --root .` on the team's own notes. Real agent-written input with
   real tags [record planning/00-options-considered.md:38 "the checker's first real input is its own planning notes"].
   It likely shows all green, since 45 of 45 model citations held [record planning/02-demo-input-and-logs.md:46 "45 of 45 held across A, B and C"]; the demo says so.
2. **Staged, and said to be staged:** add three real lines at the top of `planning/00-options-considered.md` (a
   dated "update" note), `git diff` on screen, re-run: every tag into that file turns "wrong line", each with its
   new place, as measured on other files [record planning/02-demo-input-and-logs.md:54 "10 of 15 hold; all 5 misses are"].
   Undo with `git checkout -- planning/00-options-considered.md`; `git status --short` prints nothing.
- Case against "both": two runs cost a minute of a five-minute demo; the staged one is planted, which 00 set out to
  avoid [record planning/00-options-considered.md:39-40 "the demo shows what it finds rather than a planted error"]. Kept
  because a file that changes after the report is the real failure, and it is said aloud as a re-enactment.

## 4. Demo script outline (`planning/demo-script.md`, ~5 minutes, the brief's p.2 order)
1. **What it does** (45 s): the problem in one line; the real run on `planning/`.
2. **Tools** (20 s): Claude Code in the terminal; a planning team of subagents (`planning/0*.md`); /build with a reviewer per commit.
3. **How the agent helped** (60 s): the planning files; `git log --reverse --oneline` (tests before code); one
   "helped" and one "failed, corrected" entry read from `planning/decisions.md`, never made up.
4. **Features and bugs** (60 s): seven verdicts; the staged red; `REFUSED` on an absolute path (golden row H2); one bug the tests caught.
5. **Cut** (40 s): section 8's list, three items said aloud.
6. **Weakest part** (45 s): it cannot tell a file that changed from a citation that was wrong; next, `--at <commit>`
   reading each file as it was when the report was written (`git show`).

## 5. README skeleton (seven `##` headings)
What it is (two lines and the sample output) · How to run it (no install; command; tests) · How it decides (the
seven verdicts table, the match rule in four lines) · Trade-offs (exact match, case kept, one root) · What was cut ·
Weakest part and what next · How it was built (Claude Code, `planning/`, `planning/decisions.md`, `logs/`, and whether
the logs are there and scrubbed, or why not; the brief allows "If exporting logs fails, that is fine. Mention it in
your submission." [source: the assessment brief p.2, read 2026-11-07]).

## 6. `planning/decisions.md`, written as things happen (the entry below is a made-up example)
```
## 14:05 Golden row 20 expected one place, the file has two
- Agent did: wrote the "found at" test with a single place
- Helped / failed: failed; the fixture has "water the plants" on lines 1 and 3
- Corrected by: Danish read the failure; the test now expects both places
- Commit: abc1234
```
One entry per real moment; time from `date +%H:%M`; "Commit: none" when nothing was committed.

## 7. Session fence and the scrub step
- **Fence (02's pick):** `--settings` with `permissions.blockReadsOutsideWorkingDirectories: true` and a `Read(...)`
  deny on `~/Documents` for file tools, plus `sandbox.filesystem.denyRead` on `~/Documents` and `~/Developer` with
  allowRead on the repo for the shell [record planning/02-demo-input-and-logs.md:109 "blockReadsOutsideWorkingDirectories: true"].
  Installed Claude Code is 2.1.319, past the v2.1.257 that setting needs [measured, claude --version, 7 Nov].
- **Known cost, now confirmed:** /build names a rules file outside the repo; the fence blocks it, as 02 warned
  [record planning/02-demo-input-and-logs.md:111 "may break a skill or hook that reads its own files through a tool"].
  The brief restates that rule in plain words, so nothing outside the repo is read [measured, read of the /build skill file].
- **Test (ii), shell half, two branches.** If either rule stops `cat`: keep the settings as drafted. If neither does:
  task 0 changes; the sitting keeps Danish's own permission mode so each shell command is shown before it runs, the
  brief's "only this repo" rule stands, and the scrub's private-list check (pass 5) is the backstop; the README says so.
- **Test (i), two branches.** If `/export` carries start-up blocks: task 7's pass 1 uses the markers the test found,
  and its test log holds one of each. If not: pass 1 still runs on the four known markers (cheap; guards a later
  change) [record planning/02-demo-input-and-logs.md:125 "Final marker list comes from test (i)"]. Either way the
  submitted log is the `/export` text [record planning/02-demo-input-and-logs.md:113 "the /export text, scrubbed"].
- **The scrub in the sitting:** `python3 scrub.py <export> <scrubbed-out> <private-list> <report-out>`, 02's five
  passes [record planning/02-demo-input-and-logs.md:118 "about 40 lines, one test"]; the sitting builds and tests it
  on a made-up log only. Danish runs it on the real export after the session ends, so the private list never enters
  the session or its log; the report goes outside the repo; he reads it and the scrubbed export before any push
  [record planning/02-demo-input-and-logs.md:149 "Danish reads the scrubbed export in full before any push"].
- **What the log cannot show:** anything after `/export` (the scrub run, the merge); the README says so.

## 8. Cut
`path:line:col`, `#L12` anchors, URLs and paths with spaces [record planning/01-prior-art-and-formats.md:33 "URLs, paths with spaces"];
`...` in quotes [record planning/01-prior-art-and-formats.md:59 "Taken literally (cut)"]; fuzzy or case-blind
matching; a "near line" tolerance; an "also at" note when a green quote repeats; JSON output; a package or CI; any
model call at run time [record planning/00-options-considered.md:35 "no model call at run time"].

## 9. Not settled
- Test (i) and the shell half of test (ii): Danish's script, this wave.
- Where Danish's private list lives (outside the repo); the brief writes it `<private-list>`.
- Whether `.claude/settings.json` in the repo is committed; whether the sitting's STATE file sits at `planning/STATE.md`.
- The start script names the brief by an absolute path built at run time, not `planning/build-brief.md`: /build's
  merge guard looks for a path starting with `/` in the first message [measured, read of the /build skill's merge hook, 7 Nov].
- How the summary counts "not checked" (one per skipped backtick span or URL holding a path shape) [assumed].
