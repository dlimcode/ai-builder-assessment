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

## Lows
