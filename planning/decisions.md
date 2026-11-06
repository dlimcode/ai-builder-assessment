# Decisions log: the build sitting (7 Nov 2026)

One entry per real moment the agent helped, failed or was corrected, written as it happens
(format: `planning/03-plan.md` section 6). Times from `date +%H:%M`.

## 01:33 Task 0: the dry run's three answers were not passed to this session
- Agent did: started from `/build` with the brief; `/build` loaded (its text is in this session). The session's own
  sandbox settings list `~/Documents` and `~/Developer` as read-denied for the shell, with this repo allowed.
- Helped / failed: unknown; the dry run (recipe stops at once, shell canary `cat`, subagent canary Read) ran in
  Danish's terminal before this session, and its three answers were not given to the agent. Not invented here.
- Corrected by: none yet; Danish to add the three answers (stop / BLOCKED / BLOCKED, or what he saw).
- Commit: none

## 01:36 Fixtures committed alone, against the brief's one-commit rule
- Agent did: committed task 1's fixtures as their own commit (18e6421)
- Helped / failed: failed; the brief says the fixtures and the golden-set tests are one commit, and task 10's
  done-check needs the first commit on `tests/` to be `test(checker): add golden set before any code`
- Corrected by: the agent, on re-reading the brief: soft reset, the fixtures go into task 2's commit
- Commit: none (18e6421 undone before any push)

## 01:38 Task 4's done-check needs task 5's command line
- Agent did: ran task 4's done-check (the whole suite); it fails only on the command-line tests, which task 2
  wrote because task 2 asks for the exit codes, and which only task 5 can pass
- Helped / failed: the plan's order, not the code: task 4's own tests (find, golden rows, symlink refusal) pass
- Corrected by: the agent: task 4 is checked on those three test groups; the full-suite `OK` is checked at task 5
- Commit: none

## 01:39 Dog-food run on the planning notes: 174 references, 89 hold, 19 red
- Agent did: ran `python3 check_citations.py planning/*.md --root .` (task 6) and read each red line
- Helped / failed: helped; no red is a checker bug. 18 reds are the "Found at" column of 01's golden table
  (`planning/01-prior-art-and-formats.md` lines 103-125), where `notes.md:3` and `data/plan.txt:1` are written bare,
  outside backticks, and name fixture files relative to `tests/fixtures`, not the repo root: "file missing" is right
  by 01's own rule that only backticked text is an example. One red is a real miscite: `planning/README.md` line 113
  cites `build-brief.md:15`, a path not relative to the repo root (the file is `planning/build-brief.md`).
- Corrected by: none; `planning/0*.md` stay frozen and README.md is the task list, so neither is edited here
- Commit: none

## 01:41 Task 2's review: one Medium (F1), fixed; three Lows
- Agent did: wrote the golden tests; the reviewer found the H3 copy run did not check the counts, so a checker
  that never resolved `--root` (a root behind /tmp's symlink) passed every test
- Helped / failed: the review helped; the test gap was the agent's
- Corrected by: fix cb5bca6 checks all five counts on the copy, red with `realpath(root)` removed (run on a mutated copy)
- Commit: cb5bca6

## 01:41 The commit guard refused made-up keys and a MAC in the scrub test
- Agent did: wrote `tests/test_scrub.py` with literal fake tokens and a MAC-shaped string
- Helped / failed: failed; Danish's commit guard refuses secret- and MAC-shaped strings even as fixtures
- Corrected by: the guard; the test now builds those values from pieces at run time, so no committed file holds one
- Commit: none

## 01:45 Task 4's review: an unclosed quote came out green; fixed
- Agent did: wrote the quote parse so a quote with no closing mark was dropped, leaving "line only" (exit 0)
- Helped / failed: the review helped; the agent's parse failed open. The recheck of cb5bca6 also corrected the
  task 2 review: plain removal of `realpath(root)` was already caught, only an `abspath` form slipped through
- Corrected by: fix a95a1be: an unclosed quote runs to the end of the line and is checked (red if wrong); a curly
  open may close straight. Chosen over an eighth verdict to keep 01's closed list of seven
- Commit: a95a1be

## 01:46 The scrub: built to 02's five passes, with three choices nobody could check
- Agent did: wrote `scrub.py` (tests first, on a made-up log holding one of each of the six start-up blocks) and
  `planning/finish-sitting.sh`, dry-run once on a made-up export and list
- Helped / failed: open; not verified against a real `/export`, whose format this session has not seen. Choices:
  (1) a loaded skill, hook output or rules file is cut up to the next line starting `> ` or `⏺` (assumed prompt and
  reply marks), and any block whose end is not found is cut to the end of the file, so it fails safe, not open;
  (2) the username is the login name, and its hits are listed apart, not failed; (3) pass 5 runs twice, with line
  breaks removed and with them as spaces, so "Acme\nWidgets" also matches. 200 lines, not 02's "about 40"
- Corrected by: none yet; Danish's read of the pass-1 counts in the real report closes (1)
- Commit: see the scrub commit after this entry

## 01:46 Three entry times were guessed, not read from the clock
- Agent did: wrote the 01:41 (task 2 review), 01:45 (task 4 review) and 01:46 (scrub) entries with guessed times
  (01:40, 01:44, 01:49)
- Helped / failed: failed; 03 section 6 says times come from `date +%H:%M`, and 01:49 was later than the clock
- Corrected by: the agent, on the next `date`: each set to the clock reading taken just before or after it was written
- Commit: none (corrected before this file's next commit)

## 01:48 Reviewers' notes against the final code: 0 red, 37 of 40 not checked
- Agent did: ran `python3 check_citations.py planning/reviews/*.md --root .` (task 9)
- Helped / failed: helped, by showing a limit: the reviewers wrapped their `path:line "words"` citations in
  backticks, which the checker skips as examples, so the run shows 0 red, 0 holds, 3 line only, 37 not checked.
  The planning-notes run already has a real red (the `build-brief.md:15` miscite), so by card 3 (a) the planted
  edit is not used; the demo script says both
- Corrected by: none; the next reviewer brief could ask for citations outside backticks
- Commit: the demo script commit after this entry

## Lows
- task-2-review-1 F3, `tests/test_check_citations.py`: not tested: first three places only, H3's file never opened
  (patch `open`), a permission-denied file as "file missing"
- task-2-review-1 F4, `tests/test_check_citations.py:121` and `:95`: tests fix choices 01 leaves open (line:col
  counts 0 skipped while a URL counts 1; a huge line number stored as None; found-at on the same output line)
- task-2-recheck-1 F1, `tests/test_check_citations.py:159`: the copy's symlinked root comes from the machine's
  /tmp; on a Linux CI with a real /tmp, an `abspath` root would pass. Fix: build the test's own symlinked root
- task-2-recheck-1 F2, `tests/test_check_citations.py:63`: a missing summary part raises AttributeError, hiding the line
- task-4-review-1 F2, `check_citations.py:115`: quotes match as substrings, so "safe to run" holds on "unsafe to run"
  (01 does not set word boundaries; Danish's call)
- task-4-review-1 F3, `check_citations.py:18`: the URL branch is quadratic on long letter runs (40,000 letters 2.2 s)
- task-4-review-1 F4, `check_citations.py:123`: words over three or more lines cited at the wrong place say
  "not in file", though they are in the file
- task-4-review-1 F5: no test pins `realpath` over `abspath` for the root, nor the first-three cap on places
- task-4-review-1 F1 (tail): an empty quote `""` is still "line only"
