# 04 Devil's advocate on the build plan (7 Nov 2026)

**Outcome: the plan holds and the read fence does not break the build recipe, but four things will hurt in the
sitting if not fixed first: the task file the brief points to does not exist, the cut line is too late and cuts the
wrong thing, reviewer replies and commit messages go public unscrubbed, and "resolve then check" is not pinned down.
Every fix below costs minutes, not a re-plan.**

Tags as in 01-03: `[Danish]`, `[record path:line "words"]`, `[measured, how]`, `[source, date read]`, `[assumed]`.
"The build recipe" is Danish's own build skill; findings about it are from one read of its files, never copied here.

## 1. Findings, ranked

| # | Finding | Hits in 03 | Sev. | Fix | Cost |
|---|---|---|---|---|---|
| F1 | The brief says to follow a task list in `planning/README.md` [record planning/build-brief.md:15 "task list, in order"]; that file does not exist [measured, ls planning/, 7 Nov 00:50]. With no task list, the build recipe writes its own plan, in its own words, to the brief's plan file or a default folder outside `planning/` [measured, read the build recipe, 7 Nov]: 10-15 unplanned minutes and a plan that drifts from 03 [assumed]. | [record planning/03-plan.md:59 "whose tasks must be headed"] | high | Wave 4 writes the file before the sitting: 03 section 2 as `### Task N:` headings, each with minutes and done-check. Name it `planning/tasks.md` (a README that is a task list misleads a stranger) and change brief line 15 to match. | 10 min, before the sitting |
| F2 | Cut line too late, wrong first cut. Task 4 is planned to end at 100; the cut fires at 120 [record planning/03-plan.md:55 "by minute 120, cut in this order"]. At 120, tasks 5-14 still need 120 planned minutes, so the buffer is gone before any cut [measured, re-added 03's minutes]. The first cut, folder input, breaks task 6 and the demo's real run, both of which pass a folder [record planning/03-plan.md:64 "python3 check_citations.py planning/ --root ."]. | 03 lines 55-57 | high | Cut line at minute 105. Drop folder input from the plan entirely: take one or more file arguments and let the shell expand `planning/*.md` (no folder walk, no symlink loops, less code). Cut order: colour, then rows 9-10 and 23 as expected failures, then two unit-end reviewers of three. | 3 min, edit 03/tasks |
| F3 | Reviewer replies are saved word for word into `planning/reviews/` [measured, read the build recipe, 7 Nov] and commit bodies are free text; both are committed and public, but the scrub only touches the exported log. A reply quoting the temp folder it reviewed in carries an absolute path, against [record planning/build-brief.md:52 "No absolute paths in committed files"]. The recipe also adds a session-id trailer to each commit [measured, read the build recipe, 7 Nov]. | 03 section 7, task 13 | high | Before any push, Danish runs the scrub's private-list pass (pass 5) over every tracked file and over `git log --format=%B`; a hit is fixed by a new commit, or by rewriting the branch before it is ever pushed. Say in the README whether the session trailer stays. | 5 min in task 7 (accept many inputs), 2 min at the end |
| F4 | "Refuse outside root" has no method written down [record planning/03-plan.md:40 "refuse outside root before opening"]. A string-prefix check passes a sibling folder whose name starts with the root's name; resolving only the target (not the root) refuses everything in macOS temp folders, because the system temp folder sits under a symlinked top-level folder [measured, readlink of that folder, 7 Nov]; H3's test copy lives in exactly such a folder. | 03 task 4; 01 row H3 | high | One line in the tasks: `root = os.path.realpath(root)`; `target = os.path.realpath(os.path.join(root, p))`; refuse unless `os.path.commonpath([root, target]) == root`; then refuse unless `os.path.isfile(target)`; only then open, with `encoding="utf-8"`. Add golden row H5: a sibling folder `fixtures-evil/` with a reference `../fixtures-evil/x.md:1` (refused). | 5 min |
| F5 | Golden set has no row for a path that is a folder, a binary file, or a non-regular file (a named pipe would make `open()` wait forever) [measured, read 01 rows 1-26 and H1-H4]. 01 promises binary falls into "file missing" [record planning/01-prior-art-and-formats.md:72 "not a readable UTF-8 text file"] but no test holds it to that. | 03 task 2 | medium | Rows H6 `data/:1 "x"` (folder) and H7 `bin.dat:1 "x"` (three invalid UTF-8 bytes), both "file missing", no traceback. The pipe case is covered by the `isfile` check in F4; no fixture needed. | 5 min |
| F6 | Unit end is 20 minutes [record planning/03-plan.md:47 "three fresh reviewers on the branch, fixes"], but the recipe also runs a background review on every commit, fixes every Medium-or-worse finding in its own commit, and rechecks each fix with a fresh reviewer [measured, read the build recipe, 7 Nov]. None of that has minutes in 03 [measured, read 03 section 2]. With about 15 commits, three or four Medium findings is plausible, 5 min each [assumed]. | 03 tasks 3-11 | medium | Put the per-commit fix waves in the buffer explicitly (20 of its 20 minutes), and make the unit end 30, taken from the cut list in F2. Or tell the brief: per-commit review on tasks 2, 4 and 7 only. | 2 min |
| F7 | The recipe keeps its own decisions file, in a format different from 03 section 6, with a `## Lows` heading, at a default path outside `planning/` [measured, read the build recipe, 7 Nov]; the brief maps reviews, unit report and state into `planning/` but not this file [measured, read build-brief.md lines 39-40]. | 03 section 6, task 12 | medium | One brief line: "The recipe's decisions file is `planning/decisions.md`; its Lows go under `## Lows` there." Task 12's heading count then includes that heading. | 1 min |
| F8 | Reviewers read a `git archive` export of each commit, which the recipe puts in a temp folder [measured, read the build recipe, 7 Nov]. Under the fence, file tools refuse reads outside the working folders [source: code.claude.com/docs/en/settings-reference, read 2026-11-07]; sandboxed shell commands can still read the session temp folder [same source]. So reviewers fall back to `cat`, or report "could not read" [assumed]. | 03 section 7 | medium | Brief line: "Export each commit for review into `.review/` in the repo (git-ignored), not a temp folder." Add `.review/` to `.gitignore` in task 0. | 2 min |
| F9 | The scrub is built on a made-up log and first meets the real export after the session, with no agent to fix it [record planning/03-plan.md:119 "Danish runs it on the real export after the session ends"]. Two gaps: a path split by terminal wrapping escapes passes 2 and 5 [record planning/02-demo-input-and-logs.md:147 "text split across lines by terminal wrapping"]; and the build recipe's own text, loaded when `/build` runs, may appear in the export without the marker pass 1 looks for [assumed until test (i)]. | 03 section 7, task 13 | medium | Pass 5 also searches the text with all line breaks removed. Test (i) must invoke `/build` itself (with an empty request it stops at once) so the real marker is known; the private list carries the recipe's distinctive file names. Pin the scrub's arguments: 02 has three [record planning/02-demo-input-and-logs.md:119 "python3 scrub.py <export> <private-list> <report-out>"], 03 has four [record planning/03-plan.md:117 "<export> <scrubbed-out> <private-list> <report-out>"]; keep 03's. | 5 min |
| F10 | Demo red is planted. The real run likely shows all green [record planning/03-plan.md:66 "It likely shows all green"]; the staged edit goes against 00's aim [record planning/00-options-considered.md:39-40 "the demo shows what it finds rather than a planted error"]. A real source of drift exists in the sitting: reviewer replies cite code lines, and later fix commits move those lines [assumed]. | 03 section 3 | medium | Brief line: reviewers cite evidence as `path:line "words"`. Demo: real run on `planning/`, then a run on `planning/reviews/*.md` against the final code; any red is a real, unplanted "cited before the code moved". Keep the staged edit only as the fallback if that run is all green. Case against: reviewer citations may not move at all, so the fallback may be needed anyway. | 1 min |
| F11 | Python and platform: `os.path.realpath(..., strict=True)` is 3.10+ and fails on 3.9.6 [assumed, from Python's changelog]; `open()` without `encoding="utf-8"` breaks the curly-quote row on systems whose default is not UTF-8 [assumed]; newer Pythons refuse to turn a digit run over 4,300 digits into a number, so a long line number crashes there but not on 3.9.6 [assumed]. `timeout` is a Homebrew tool here, not stock macOS [measured, command -v timeout]. | 03 section 1 | low | Tasks say: explicit `encoding="utf-8"`; line numbers matched as at most 9 digits, longer ones "no such line" (H4 still holds); no `strict=`. README commands use no `timeout`. | 2 min |
| F12 | Done-checks quote output that macOS prints differently: `wc -l <` prints leading spaces, `ls` of a missing file prints a longer message on stderr [assumed, from macOS `wc` and `ls` behaviour]. | 03 tasks 1-2 | low | Write the checks as `[ "$(wc -l < f \| tr -d ' ')" = 9 ] && echo ok`; `test ! -e check_citations.py && echo absent`. | 3 min |
| F13 | A crash mid-sitting: rerunning the start script opens a new session, so the export holds only the second half [assumed]. | 03 task 13 | low | Export both sessions if it happens; the README says so. No script change. | 0 |

## 2. Fancy for its own sake?
- No: it is a grep for quoted words at a cited line, a known kind of check (link checkers do it for links) applied to
  a format nobody checks yet [record planning/01-prior-art-and-formats.md:3 "no tool found checks"]. Plain, standard
  library, one file.
- 30-second test: the README skeleton opens with "What it is (two lines and the sample output)" [record planning/03-plan.md:86 "What it is (two lines and the sample output)"].
  The risk is the word "citation", which reads as academic references [assumed]. First line, then: "Checks that the
  words an AI report quotes are really on the file line it cites."

## 3. Security, case by case
| Case | Golden row | Plan covers it? |
|---|---|---|
| `..` out of the root | H1 | yes, if F4's method is used |
| Absolute path | H2 | yes (resolves outside the root) |
| Symlink out of the root | H3 | yes, once the root itself is resolved (F4) |
| Sibling folder sharing the root's name prefix | none | no: add H5 (F4) |
| Huge line number | H4 | yes; cap digits (F11) |
| Path that is a folder | none | no: add H6 (F5) |
| Binary or non-UTF-8 file | none | promised, not tested: H7 (F5) |
| Named pipe or device inside the root | none | only via the `isfile` check (F4) |
| Huge file inside the root | none | not covered; whole file read into memory. Accept for v1 and say so in the README [assumed: reports cite source files, not multi-gigabyte data] |
| Folder of thousands of files | n/a once F2 drops folder input | the shell expands the glob; nothing to walk |
| Report text with terminal control codes echoed in output | none | low; strip characters below space except tab when printing [assumed] |

## 4. Minutes, re-added
- Task minutes 5+15+25+25+30+15+10+20+15+10+5+20+5+15+5 = 220; tasks 7, 8, 9, 12, 13 = 65; tasks 1-6 = 120. All
  three of 03's sums are right [measured, re-added by hand from 03 section 2] [record planning/03-plan.md:52 "tasks 7, 8, 9, 12, 13 = 65 minutes"].
- Not counted: the recipe's per-commit fix waves (F6); the recipe writing its own plan if F1 is not fixed; Danish
  reading the README and decisions log, which carry his explanation of where the AI helped [assumed: 10 min].
- 65 minutes for writing work is fair for agent-written drafts; the scrub at 20 is tight, since pass 5's report and
  the username section push it past 02's 40 lines [assumed].
- 20 minutes for three reviewers, fixes and re-reviews is not real; 30 is [assumed]. The cut line: see F2.

## 5. Works only on this Mac?
- The start script builds every path at run time and needs only bash, git, python3 and claude [record planning/start-sitting.sh:3 "Every absolute path is built at run time"].
- It stops while main has no commit [record planning/start-sitting.sh:19 "main has no commit yet"]; main has none today
  [measured, git log, 7 Nov 00:51]. Danish commits `planning/` first; `.claude/` stays out of that commit.
- The merge hook needs `jq`; it is present [measured, command -v jq]. If it were missing, the hook would pass every merge [measured, read the build recipe, 7 Nov].
- Python items: F11. Done-check output: F12.

## 6. The read fence, checked at source
**Verdict: the fence does not stop the recipe loading, its hook running, or its reviewers starting. One thing
fails (reviewers' file tools on a temp export, F8) and one is skipped by design (the outside rules file).**

| Part of the recipe | Under the fence | Why |
|---|---|---|
| Loading `/build` (symlinked from `~/.claude/skills` into a folder under `~/Developer`) | works [assumed until the dry run below] | "Files Claude Code itself needs stay readable, such as your skills" [source: code.claude.com/docs/en/settings-reference, read 2026-11-07]; loading is Claude Code's own read, not a file tool [assumed] |
| Its merge hook (a script in its own folder) | works | Hooks "run with your full access", outside the sandbox [source: code.claude.com/docs/en/sandboxing, read 2026-11-07]; it reads the session's transcript and the brief, both reachable that way [measured, read the build recipe, 7 Nov] |
| Its reviewers | start | No custom agent folder exists, so the recipe falls back to general-purpose agents [measured, ls of ~/.claude, 7 Nov]; reading their export: F8 |
| Its outside rules file | blocked | as 03 says; the brief restates the rule [record planning/build-brief.md:30 "in place of the recipe's outside rules file"] |
| A worktree beside the repo | blocked | Under the block, sandboxed commands lose the whole home folder and get back only the working folders, worktrees Claude Code makes, the session temp folder and the needed parts of `~/.claude` [source: code.claude.com/docs/en/settings-reference, read 2026-11-07] |

- **03's three claims about the recipe:** worktree: partly right. The recipe makes a sibling worktree when there
  is no brief or no branch; with a brief naming a branch it works on that branch [measured, read the build recipe, 7 Nov],
  so switching the checkout first is right [record planning/03-plan.md:60 "Its worktree step would make a folder beside the repo"].
  Merge guard: right; it reads the first message for a `.md` path starting with `/` [measured, read the build recipe, 7 Nov].
  The thread that merges (task 14) must also be started with the brief's full path, and the merge needs a switch
  to main, which the hook checks [same read]. `### Task N:` headings: right [same read], but see F1.
- **The smallest fence:** `blockReadsOutsideWorkingDirectories: true` plus `sandbox.enabled: true`. With both on,
  the sandbox already denies the whole home folder to shell commands [source: code.claude.com/docs/en/settings-reference, read 2026-11-07],
  so the script's `denyRead`/`allowRead` lines and the Documents `Read` deny are redundant but harmless
  [record planning/start-sitting.sh:47 "denyRead"]. Keep them as a second lock if test (ii) shows the sandbox does not
  start at the desk [assumed]. **Do not add `allowRead` on the harness folder:** nothing in the run needs it, and it
  would let private recipe text into the session and its public log.
- **Dry run, 1 minute, before the sitting:** start the script's settings with `/build` and no request; the recipe
  stops at once saying there is nothing to build [measured, read the build recipe, 7 Nov]. If it answers that, it
  loaded under the fence.

## 7. Rewording for 02's flagged lines
Lines 68 and 128-130 (and line 81, which carries the home root after "Contents of"; the lead's grep did not list it
[measured, grep of planning/, 7 Nov 00:52]) spell path patterns out literally. Same meaning, no literal:
- 68: "where the folder name is the working folder with each slash turned into a dash (so it begins with the home
  folder's dash-encoded form)".
- 81: "CLAUDE.md (the `Contents of` line that names its file)".
- 128: "other temp roots (the system temp folder, its private twin, the per-user temp folder and `$TMPDIR`) to `<tmp>`".
- 129-130: "the dash-encoded forms (the repo's dash-encoded folder name to `<repo-folder>`, the home folder's
  dash-encoded form to `~`)".
- The scrub's code still needs the real patterns; they live in `scrub.py` built from `$HOME` at run time, never typed.

## 8. Not checked
- Whether `/build` loads through the symlink under the block (the dry run in section 6 settles it).
- Whether subagents inherit `--settings` [assumed: yes]; whether the sandbox starts at the desk (test (ii)).
- Whether `/export` carries the loaded recipe's text (test (i), with `/build` in it).
- Python 3.10+ behaviour of the F11 items; not run on any other Python.
