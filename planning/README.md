# The build sitting, step by step (7 Nov 2026)

**Answer: one sitting builds `check_citations.py` (one Python 3.9 file, standard library, no model call), tested by a
33-row golden set committed before any checker code, plus the log scrub and the demo script: 233 planned minutes and a
7-minute buffer, 240 in all [assumed]. The demo moment: the checker run on this folder's own notes, then a red line
with where the words really are now: reviewers' notes against the final code, the staged edit only if that is green (card 3).**

This file is the task list the build brief points to [record planning/build-brief.md:15 "task list, in order"].
Tags as in 01-04: [Danish] his words, [record path:line "words"], [measured, how], [source, date read], [assumed].
Every minute is [assumed]. "The sitting" is one desk session [Danish] ("maybe i can take 3-4 hours with this? just one
desk sitting to complete."). Each task: one commit or more, `type(scope): subject`; run its done-check before the next.
Done-checks use `timeout`, installed on this Mac [record planning/04-devils-advocate.md:25 "is a Homebrew tool here"].

## The sitting starts here

### Task 0: Fence dry run, then start (8 min)
Danish, in his own terminal: `bash planning/start-sitting.sh --dry-run`. The recipe should stop at once
[record planning/04-devils-advocate.md:92-93 "the recipe stops at once saying there is nothing to build"]. He then asks
for a shell `cat` of a one-line canary file under `~/Documents`, and one subagent reading it with the Read tool; both
should say BLOCKED. `/exit`, then `bash planning/start-sitting.sh`. In the session: add `logs/raw/` and `.review/` to
`.gitignore`, and `.claude/` (card 2: keep out); create `planning/decisions.md` with an entry holding the three
dry-run answers, and a `## Lows` heading. If the shell `cat` was READ, the sitting keeps Danish's own permission mode
[record planning/03-plan.md:111 "keeps Danish's own permission mode"]; if `/build` did not load, follow this file without it.
**Done-check:** `git branch --show-current` prints `build/check-citations`; `grep -cxE 'logs/raw/|\.review/|\.claude/' .gitignore` prints `3`.
### Task 1: Fixtures (15 min)
`tests/fixtures/`: 01's `notes.md`, `data/plan.txt`, `empty.md` byte for byte; `bin.dat` is three invalid UTF-8 bytes
(`printf '\377\376\375'`); `report.md` is 01's rows 1-26, H1-H4, then H5-H7 below, one per line. `tests/fixtures-evil/x.md` holds `x`.

| # | Reference | Expected | Tests |
|---|---|---|---|
| H5 | `../fixtures-evil/x.md:1 "x"` | refused: outside root | sibling folder whose name starts with the root's name [record planning/04-devils-advocate.md:18 "Add golden row H5"] |
| H6 | `data/:1 "x"` | file missing | path is a folder [record planning/04-devils-advocate.md:19 "Rows H6"] |
| H7 | `bin.dat:1 "x"` | file missing | not UTF-8 text, no traceback |

**Done-check:** `for f in notes.md report.md; do wc -l < tests/fixtures/$f | tr -d ' '; done` prints `9` then `33`;
`wc -c < tests/fixtures/bin.dat | tr -d ' '` prints `3`; `test -f tests/fixtures-evil/x.md && echo ok` prints `ok`.
### Task 2: Golden-set tests, red (25 min)
`tests/test_check_citations.py`: the 33 rows as one table; CLI exits 0/1/2 (a folder argument is a usage error, 2).
H3: copy `tests/fixtures` and `tests/fixtures-evil` into a `tempfile` folder, add `link-out.md` pointing outside the
copy's root, run the report there (on the repo copy H3 is "file missing", still red). Expected summary: 33 references,
10 holds, 1 line only, 20 red, 2 not checked, exit 1 [record planning/01-prior-art-and-formats.md:134 "10 holds, 1 line only, 17 red, 2 not checked"], plus H5-H7 red.
Run, see it fail, commit `test(checker): add golden set before any code`. Per-commit review: yes.
**Done-check:** `timeout 120 python3 -m unittest discover -s tests 2>&1 | tail -1` starts with `FAILED`; `test ! -e check_citations.py && echo absent` prints `absent`.
### Task 3: Find references (25 min)
Path shape, `[record ...]` wrapper, first straight or curly quote right after the line number, skip backticks, fences
and URLs. Line numbers: a digit run longer than 9 is "no such line" without `int()` (H4).
**Done-check:** `timeout 60 python3 -m unittest tests.test_check_citations.FindTests 2>&1 | tail -1` prints `OK`.
### Task 4: Match, verdicts, root check (30 min)
Cleaning, two-line quote, range, whole-file search (first three places). Root check before any open, exactly:
`root = os.path.realpath(root)`; `target = os.path.realpath(os.path.join(root, p))`; refused unless
`os.path.commonpath([root, target]) == root`; "file missing" unless `os.path.isfile(target)`; then open with
`encoding="utf-8"`, a decode error is "file missing". No `strict=`: Python 3.9 `realpath` takes only the path
[measured, inspect.signature on this Mac's python3, lead, 7 Nov 00:56]. Per-commit review: yes.
**Done-check:** `timeout 120 python3 -m unittest discover -s tests 2>&1 | tail -1` prints `OK` (or `OK (expected failures=3)` after a cut).
**Cut line, minute 105** [record planning/04-devils-advocate.md:16 "Cut line at minute 105"]: if not `OK`, cut in this order
and say so in the README: colour; rows 9-10 and 23 as `expectedFailure` with a reason; two of the three unit-end
reviewers. Never cut H1-H7 or the exit codes. Folder input is not planned at all (task 5).
### Task 5: Command line (10 min)
`python3 check_citations.py REPORT.md [REPORT.md ...] [--root DIR]`: file arguments, the shell expands `planning/*.md`,
no folder walk. Summary line names the root; colour only on a terminal; characters below space except tab stripped
when printing [record planning/04-devils-advocate.md:50 "strip characters below space except tab when printing"].
**Done-check:** `timeout 60 python3 check_citations.py tests/fixtures/report.md --root tests/fixtures; echo "exit $?"`
ends with the summary line (33 references) then `exit 1`; with `tests/fixtures` as the argument it prints `exit 2`.
### Task 6: Dog-food (10 min)
`timeout 60 python3 check_citations.py planning/*.md --root .`; each red is a checker bug (fix with a test) or a real
miscite (an entry in decisions; never edit `planning/0*.md`).
**Done-check:** `git status --short planning/0*.md` prints nothing.
### Task 7: Scrub step (25 min)
`scrub.py <export> <scrubbed-out> <private-list> <report-out>`, 02's five passes; pass 5 also runs on the text with all
line breaks removed [record planning/04-devils-advocate.md:23 "Pass 5 also searches the text with all line breaks removed"].
`scrub.py --check-only <private-list> <report-out> FILE...` runs pass 5 alone over many files. `planning/finish-sitting.sh
<private-list>` makes a temp folder (`mktemp -d "$TMPDIR/scrub.XXXXXX"`), scrubs `logs/raw/session.txt` into
`logs/session.txt`, then checks every `git ls-files` file and `git log --format=%B main..HEAD`; reports stay in the
temp folder. Tests on a made-up log only, holding one of each of the six start-up blocks a saved session file was
measured to carry (listed under What nobody could show); if `/export` fails, scrub the saved session file instead. Per-commit review: yes.
**Done-check:** `timeout 60 python3 -m unittest tests.test_scrub 2>&1 | tail -1` prints `OK`; `bash -n planning/finish-sitting.sh && echo ok` prints `ok`.
### Task 8: README.md (15 min)
03 section 5's seven headings; first line from 04 [record planning/04-devils-advocate.md:35 "words an AI report quotes are really on the file line it cites"].
Also: file arguments only; whole files read into memory [record planning/04-devils-advocate.md:48 "Accept for v1 and say so in the README"];
whether commit session trailers stay; commands without `timeout`.
**Done-check:** `grep -c '^## ' README.md` prints `7`.
### Task 9: Demo script (10 min)
`planning/demo-script.md`: 03 section 4's six points; the red moment by card 3 (a): planning notes, then reviewers' notes; the staged edit, said aloud, only if both are green. Run
`timeout 60 python3 check_citations.py planning/reviews/*.md --root .` now and write down what it shows.
**Done-check:** `grep -c '^## ' planning/demo-script.md` prints `6`.
### Task 10: Clean clone (5 min)
`tmp=$(mktemp -d "$TMPDIR/clone.XXXXXX") || exit 1; git clone -q . "$tmp/r" && (cd "$tmp/r" && timeout 120 python3 -m unittest discover -s tests 2>&1 | tail -1); [ -n "$tmp" ] && [ -d "$tmp" ] && rm -rf "$tmp"`
**Done-check:** that prints `OK`; `git log --reverse --format=%s -- tests check_citations.py | head -1` prints `test(checker): add golden set before any code`.
### Task 11: Unit end (30 min)
Three fresh reviewers on the branch, fixes, `planning/unit-report.md` [record planning/04-devils-advocate.md:20 "make the unit end 30"].
**Done-check:** `test -f planning/unit-report.md && echo present` prints `present`.
### Task 12: Decisions read-through (5 min)
Each entry has a time and a commit or "none"; re-run task 9's reviews check and update the demo script if it changed.
**Done-check:** `grep -c '^## ' planning/decisions.md` prints `7` or more (six entries and `## Lows`) [assumed].
### Task 13: Export and scrub (15 min)
`/export logs/raw/session.txt`, `/exit`. Danish: `bash planning/finish-sitting.sh <private-list>`; he reads both reports
and the scrubbed log in full [record planning/02-demo-input-and-logs.md:149 "Danish reads the scrubbed export in full before any push"];
a hit is fixed by a new commit (nothing is pushed yet); then he commits `logs/session.txt`. After a crash and restart,
export both sessions and say so [record planning/04-devils-advocate.md:27 "Export both sessions if it happens"].
**Done-check:** `git ls-files logs` prints only `logs/session.txt`; each report's last line is `private list: 0 hits`.
### Task 14: Merge (5 min)
Danish writes `yes` under the brief's `question:`, then runs `bash planning/start-sitting.sh` again, which names the
brief's full path [record planning/04-devils-advocate.md:84 "must also be started with the brief's full path"]; the agent switches to main and merges.
**Done-check:** `git log main --oneline -1` shows the merge.

**Minutes:** 8+15+25+25+30+10+10+25+15+10+5+30+5+15+5 = 233, plus a 7-minute buffer for per-commit fixes = 240.
Checker (tasks 1-6) 115; writing and logs (7, 8, 9, 12, 13) 70 [assumed, added by hand twice].

## Conflicts between the documents

| This | Against | Resolution | Whose call |
|---|---|---|---|
| 04 F1: name the list `planning/tasks.md` [record planning/04-devils-advocate.md:15 "a README that is a task list misleads a stranger"] | build-brief.md:15 and the team brief | Adapted: the list is this file, headed `### Task N:`; F1 is fixed by writing it | team |
| 03 cut at 120, folder first [record planning/03-plan.md:55 "by minute 120, cut in this order"] | 04 F2 | Taken: cut at 105; folder input dropped [record planning/03-plan.md:13 "A folder means every"] | team |
| 03 unit end 20 [record planning/03-plan.md:47 "three fresh reviewers on the branch, fixes"] | 04 F6 | Adapted: unit end 30; per-commit review on tasks 2, 4, 7 only [record planning/04-devils-advocate.md:20 "Or tell the brief: per-commit review on tasks 2, 4 and 7 only"]; 7-min buffer | team; Danish may restore every-commit review (~10 min [assumed]) |
| 02 scrub, three arguments [record planning/02-demo-input-and-logs.md:119 "python3 scrub.py <export> <private-list> <report-out>"] | [record planning/03-plan.md:117 "<export> <scrubbed-out> <private-list> <report-out>"] | 03's four, as 04 F9 says | team |
| 01 [record planning/01-prior-art-and-formats.md:4 "a 26-row golden set"] | [record planning/01-prior-art-and-formats.md:99 "rows 1-26 plus H1-H4"]; [record planning/03-plan.md:37 "rows 1-26 then H1-H4"] | 30 rows in 01, 33 with H5-H7 | team |
| 03's staged red [record planning/03-plan.md:67 "Staged, and said to be staged"] | [record planning/00-options-considered.md:39-40 "the demo shows what it finds rather than a planted error"]; 04 F10 | Card 3, answered: a (staged edit only as fallback) | Danish |
| 03 task 6 check on [record planning/03-plan.md:42 "git status --short planning/"] | decisions.md and reviews also change there | Adapted: check only `planning/0*.md` | team |
| 04 F11: no `timeout` [record planning/04-devils-advocate.md:25 "README commands use no"] | the team brief: hangs get `timeout` | Product README: none; this file's checks: `timeout` | team |
| 02 "also at" note [record planning/02-demo-input-and-logs.md:52 "line but worth an"] | [record planning/03-plan.md:127 "note when a green quote repeats"] | Cut stands (03) | team |
| 04 F7 recipe's decisions format | 03 section 6 | 03's entry format; Lows under `## Lows` [record planning/04-devils-advocate.md:21 "its Lows go under"] | team |
| 04 F3 scrub tracked files and messages [record planning/04-devils-advocate.md:17 "over every tracked file"] | 03 scrubs the export only | Taken via `finish-sitting.sh`; README states the session trailer | team |
| 04 F9: test (i) must run `/build` | the test script is outside this repo | Adapted: card 1 | Danish |
| 04 F4, F5, F8, F12, F13 | 03 | Taken as written (tasks 0-5, 13) | team |

## What nobody could show

| Gap | What closes it |
|---|---|
| Test (ii), shell half: run 01:16, a fenced `cat` was BLOCKED on both targets in both fenced runs (READ in the control), but the block came from Danish's automatic permission check, not provably from the deny rule or the sandbox [measured, Danish's test script, 7 Nov 01:16] | Task 0's shell canary, in the real sitting |
| `/build` loading through its symlink under the fence [record planning/04-devils-advocate.md:108 "loads through the symlink under the block"] | Task 0 dry run |
| Subagents inheriting `--settings` [record planning/04-devils-advocate.md:109 "Whether subagents inherit"] | Task 0: the subagent canary read |
| The sandbox starting at the desk; nested runs failed [record planning/02-demo-input-and-logs.md:99 "enabled but failed to initialize"] | Task 0: the shell canary `cat` |
| Test (i): `/export` does not run in print mode ("isn't available in this environment"), so what it carries is still unknown; the saved session file carries every start-up block: the sandbox text, the skills list, the loaded recipe's own text, start-up hook output, the global rules file, and the home path 7 times [measured, Danish's test script, 7 Nov 01:16, counts only] | Task 7's pass 1 cuts all of these; task 13's pass-1 counts and Danish's full read |
| Wrapped paths escaping the scrub [record planning/02-demo-input-and-logs.md:147 "text split across lines by terminal wrapping"] | Pass 5 on joined text (task 7); Danish's read |
| A fresh report going red with no edit [record planning/03-plan.md:66 "It likely shows all green"] | Task 9's reviews run |
| The recipe reading `### Task 0:` and these minutes | The sitting itself; log in decisions |

## Cards: only what Danish decides

**Card 1: Run the test script first**
**What it is:** whether you run your tests (i) and (ii) script before the sitting, with `/build` (no request) added to test (i)'s session.
**Where it comes from:** not run [measured, lead, 00:56]; [record planning/04-devils-advocate.md:23 "Test (i) must invoke"].
**Your options:** (a) run it first, about 5 min [assumed]; nothing to undo. (b) skip: task 0 covers test (ii), the real export answers test (i) after the sitting; undone by running it any time before a push.
**My pick and the case against it:** (a): task 7 then cuts the right blocks with an agent at hand. Against: it edits a script outside this repo and costs minutes the dry run half covers.
**Your answer:** `test script: run first` or `test script: skip`. Answered 7 Nov ~01:10: "run first" [Danish]; run 01:16.

**Card 2: Keep `.claude/settings.json` out of git**
**What it is:** whether the repo's Claude Code settings (one line, the commit co-author) go public with the repo.
**Where it comes from:** [record planning/03-plan.md:133 "in the repo is committed"]; [record planning/04-devils-advocate.md:64 "stays out of that commit"].
**Your options:** (a) keep out: task 0 adds `.claude/` to `.gitignore`; undone by deleting that line. (b) commit it; undone by `git rm --cached` before a push.
**My pick and the case against it:** (a): nothing in it helps a reader. Against: it holds nothing private, and showing the set-up is honest.
**Your answer:** `settings: keep out` or `settings: commit`. Answered 7 Nov ~01:25: "your picks" [Danish], so keep out.

**Card 3: The demo's red moment**
**What it is:** which red the demo shows, since the run on the notes will likely be all green.
**Where it comes from:** [record planning/03-plan.md:63 "The demo's red moment: both"] against [record planning/04-devils-advocate.md:24 "Keep the staged edit only as the fallback"].
**Your options:** (a) notes run, then reviewers' notes against the final code; the staged edit only if that is green, said aloud. (b) 03's: notes run plus the staged edit always. (c) real runs only, green said as green. Each undone by editing `planning/demo-script.md` before recording.
**My pick and the case against it:** (a): any red it shows is real. Against: reviewers may cite nothing that moved, so the planted fallback may run anyway.
**Your answer:** `demo red: a`, `demo red: b` or `demo red: c`. Answered 7 Nov ~01:25: "your picks" [Danish], so a.

## What the team assumed
- Every minute figure and the 7-minute buffer; per-commit fixes on three reviewed commits fit in it [assumed].
- Danish's ten minutes reading README and decisions [record planning/04-devils-advocate.md:56 "reading the README and decisions log"] happen while task 11's reviewers run [assumed].
- Reviewers follow the brief's `path:line "words"` rule with repo paths; the recipe accepts `### Task 0:` [assumed].
- Commit session trailers hold an id, nothing private [assumed]; the README says they stay unless Danish strips them.
- build-brief.md and start-sitting.sh were edited so every line 04 cites keeps its number [measured, script check, 7 Nov].

## Files

| Path | What |
|---|---|
| `planning/README.md`, `planning/build-brief.md` | This task list; the brief the sitting starts from |
| `planning/start-sitting.sh` | Starts the session; `--dry-run` for task 0 |
| `planning/00-04*.md` | The planning team's notes (frozen) |
| `planning/decisions.md`, `demo-script.md`, `finish-sitting.sh`; `check_citations.py`, `scrub.py`, `tests/`, `README.md`, `logs/session.txt` | Made in the sitting |
