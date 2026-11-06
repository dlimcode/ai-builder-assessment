---
skill: build
branch: build/check-citations
status: blocked-on-human
question: |
  What: merge build/check-citations into main, once the checks pass and the logs are scrubbed?
---

# Build brief: a citation checker for agent-written reports

Build `check_citations.py`: it reads a markdown report, finds each reference like `notes.md:32 "under a minute"`,
opens that file, checks the quoted words are on that line, and prints green or red, with where the words really are
when red. Python 3.9 standard library only, tests with `unittest`, no model call, no API key.

**Follow `planning/README.md`'s task list, in order.** Each task there is headed `### Task N:` with its minutes and
its done-check. Stop at the end of each task and run its done-check before the next.

## Read first, in this order, and nothing else outside this repo
1. This file.
2. `planning/README.md`: the task list.
3. `planning/01-prior-art-and-formats.md`, sections 2-5 (shapes, match rule, verdicts, golden set), plus rows H5-H7 in `planning/README.md` task 1.
4. `planning/02-demo-input-and-logs.md`, section 3: the scrub step.
5. `planning/03-plan.md`, sections 6 and 7: the decisions log format and the session fence.

## Where you work
- Only inside this repo, on the branch above, in this checkout (the start script has switched to it; no worktree,
  since a folder beside the repo is outside this session's read fence).
- Read nothing outside the repo and paste nothing from other projects. If a step of the build recipe points at a
  file outside the repo, skip that read and use the rule written here instead.
- Code rule (in place of the recipe's outside rules file): write the simplest code that does the job, change only
  what the task needs, never cut input checks or security checks, and leave one test on any risky logic.

## How you work
- **Tests first, and git shows it.** The fixtures and the golden-set tests are one commit, made before
  `check_citations.py` exists. Run them and see them fail before writing checker code.
- **Small commits**, `type(scope): subject`, imperative; the body says why.
- **`planning/decisions.md`, written as things happen, never afterwards.** Every real moment the agent helped, failed,
  or was corrected, in the format in `planning/03-plan.md` section 6. Never invent an entry; "none yet" is fine.
- The build recipe's files go in `planning/`: reviews in `planning/reviews/`, the unit report in
  `planning/unit-report.md`, and if a state file is needed, `planning/STATE.md`.

## Files you produce
- `check_citations.py`, `tests/test_check_citations.py`, `tests/fixtures/`.
- `scrub.py`, `tests/test_scrub.py` (tested on a made-up log only) and `planning/finish-sitting.sh`.
- `README.md`: what it is, how to run it, trade-offs, what was cut, the weakest part and what next.
- `planning/demo-script.md`: the six demo points in order, a few lines each, about five minutes in all.

## Secrets and private material
- `.env` and `.env.*` are already in `.gitignore`; nothing here needs a key. Never read, print or commit a secret.
- Nothing belonging to any client or employer enters this repo. The README and the demo script claim nothing
  about the author's past work.
- No absolute paths in committed files: write paths relative to the repo root, and the home folder as `~`.

## Logs
- Near the end, export this session with `/export logs/raw/session.txt` (`logs/raw/` is git-ignored).
- The scrub is run by Danish after the session ends, with his private word list kept outside the repo; he reads
  its report and the scrubbed log before anything is pushed. Only `logs/session.txt` is committed.
- Before any push, `planning/finish-sitting.sh` also checks every tracked file and every commit message
  against that private list; a hit is fixed by a new commit.
- If the export or the scrub cannot be made clean, say so in the README instead of committing the log.

## Done when
- From a clean clone, the README's commands run and `python3 -m unittest discover -s tests` prints `OK`.
- `python3 check_citations.py planning/*.md --root .` runs, and every red it shows is explained in `planning/decisions.md`.
- The log is exported and scrubbed, or the README says why not.
- `planning/demo-script.md` is written.

## Not in this sitting
Pushing, making the repo public, recording the demo, emailing anyone, and merging into `main` without Danish's
`yes` under `question:` above.

## The build recipe's own steps, set here
- **The checker takes file arguments** (`planning/*.md`, expanded by the shell); it does not walk folders.
- **Per-commit review on tasks 2, 4 and 7 only**; the other commits are covered by the three reviewers at the unit end.
- **Export each commit for review into `.review/<short sha>/` in this repo** (git-ignored), not a temp folder: file
  tools here cannot read outside the repo.
- **Reviewers cite their evidence as `path:line "words"`**, with paths relative to the repo root, never `.review/`.
- **The recipe's decisions file is `planning/decisions.md`**: entries in the format of `planning/03-plan.md`
  section 6; its Lows go under a `## Lows` heading there.
